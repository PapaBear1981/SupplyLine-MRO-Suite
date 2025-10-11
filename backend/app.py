from flask import Flask, session, jsonify
from routes import register_routes
from config import Config
from flask_session import Session
from flask_cors import CORS
from models import db
import os
import sys
import time
import datetime
import logging.config
from utils.session_cleanup import init_session_cleanup
from utils.resource_monitor import init_resource_monitoring
from utils.logging_utils import setup_request_logging

def create_app():
    # Set the system timezone to UTC
    os.environ['TZ'] = 'UTC'
    try:
        time.tzset()
        print("System timezone set to UTC")  # Keep this as print since logging not yet configured
    except AttributeError:
        # Windows doesn't have time.tzset()
        print("Running on Windows, cannot set system timezone. Ensure system time is correct.")

    # serve frontend static files from backend/static
    app = Flask(
        __name__,
        instance_relative_config=False,
        static_folder='static',
        static_url_path='/static'
    )
    app.config.from_object(Config)

    # Allow runtime overrides of the database URL (useful for tests)
    runtime_db_url = os.environ.get('DATABASE_URL')
    if runtime_db_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = runtime_db_url

    # Normalize engine options when using SQLite (particularly in tests)
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'echo': False,
            'pool_pre_ping': True,
            'connect_args': {'check_same_thread': False},
        }

    # Determine if we're running in a testing environment
    is_testing_env = bool(
        app.config.get('TESTING')
        or os.environ.get('FLASK_ENV') == 'testing'
        or os.environ.get('PYTEST_CURRENT_TEST')
    )
    if is_testing_env:
        app.config['TESTING'] = True

    # Validate security configuration (deferred to allow test fixtures to set values)
    Config.validate_security_config(app.config)

    # Configure structured logging
    if hasattr(Config, 'LOGGING_CONFIG'):
        try:
            logging.config.dictConfig(Config.LOGGING_CONFIG)
            logging.getLogger(__name__).info("Structured logging configured successfully")
        except Exception as e:
            logging.getLogger(__name__).warning("Error configuring logging: %s", e)
            # Fall back to basic logging
            logging.basicConfig(level=logging.INFO)

    # Initialize CORS with settings from config
    allowed_origins = app.config.get('CORS_ORIGINS', ['http://localhost:5173'])
    allow_headers = app.config.get('CORS_ALLOW_HEADERS', [
        "Content-Type",
        "Authorization",
        "X-CSRF-Token",
    ])
    supports_credentials = app.config.get('CORS_SUPPORTS_CREDENTIALS', False)
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": allowed_origins,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": allow_headers,
                "supports_credentials": supports_credentials,
            }
        },
    )

    # Ensure session storage is configured (default to secure filesystem storage)
    session_type = app.config.get('SESSION_TYPE')
    if not session_type or str(session_type).lower() in {'none', 'null', ''}:
        app.config['SESSION_TYPE'] = 'filesystem'

    # Initialize Flask-Session
    Session(app)

    # Initialize session cleanup
    init_session_cleanup(app)

    # Initialize resource monitoring
    init_resource_monitoring(app)

    # Setup request logging middleware
    setup_request_logging(app)

    # Initialize database with app
    db.init_app(app)

    # Get logger after logging is configured
    logger = logging.getLogger(__name__)

    # Log current time information for debugging
    logger.info("Application starting", extra={
        'utc_time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'local_time': datetime.datetime.now().isoformat()
    })

    # Run database migrations unless we're running tests
    if not is_testing_env:
        try:
            # Import and run the reorder fields migration
            from migrate_reorder_fields import migrate_database
            logger.info("Running chemical reorder fields migration...")
            migrate_database()
            logger.info("Chemical reorder fields migration completed successfully")
        except Exception as e:
            logger.error("Error running chemical reorder fields migration", exc_info=True, extra={
                'migration': 'reorder_fields',
                'error_message': str(e)
            })

        try:
            # Import and run the tool calibration migration
            from migrate_tool_calibration import migrate_database as migrate_tool_calibration
            logger.info("Running tool calibration migration...")
            migrate_tool_calibration()
            logger.info("Tool calibration migration completed successfully")
        except Exception as e:
            logger.error("Error running tool calibration migration", exc_info=True, extra={
                'migration': 'tool_calibration',
                'error_message': str(e)
            })

        try:
            # Import and run the performance indexes migration
            from migrate_performance_indexes import migrate_database as migrate_performance_indexes
            logger.info("Running performance indexes migration...")
            migrate_performance_indexes()
            logger.info("Performance indexes migration completed successfully")
        except Exception as e:
            logger.error("Performance indexes migration failed - aborting startup", exc_info=True, extra={
                'migration': 'performance_indexes',
                'error_message': str(e)
            })
            raise

        try:
            # Import and run the database constraints migration
            from migrate_database_constraints import migrate_database as migrate_database_constraints
            logger.info("Running database constraints migration...")
            migrate_database_constraints()
            logger.info("Database constraints migration completed successfully")
        except Exception as e:
            logger.error("Database constraints migration failed", exc_info=True, extra={
                'migration': 'database_constraints',
                'error_message': str(e)
            })
            # Don't abort startup for constraints migration as it's not critical

    # Setup global error handlers
    from utils.error_handler import setup_global_error_handlers
    setup_global_error_handlers(app)

    # Create database tables (after all setup is complete)
    if not is_testing_env:
        try:
            logger.info("Creating database tables...")
            with app.app_context():
                db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error("Error creating database tables", exc_info=True, extra={
                'error_message': str(e)
            })
            raise
    else:
        logger.info("Skipping automatic database table creation in testing mode")

    # Create admin user if it doesn't exist (after tables are created)
    if not is_testing_env:
        try:
            from utils.admin_init import create_secure_admin
            logger.info("Checking/creating admin user...")
            with app.app_context():
                success, message, password = create_secure_admin()
                if success:
                    logger.warning("SECURITY NOTICE: Admin user created successfully")
                    if password:
                        logger.warning("INITIAL ADMIN PASSWORD GENERATED - copy from env-var not from logs")
                else:
                    logger.error(f"Failed to create admin user: {message}")
        except Exception as e:
            logger.error("Error during admin user creation", exc_info=True, extra={
                'error_message': str(e)
            })

    # Register main routes
    register_routes(app)

    # Add security headers middleware
    @app.after_request
    def add_security_headers(response):
        security_headers = app.config.get('SECURITY_HEADERS', {})
        for header, value in security_headers.items():
            response.headers[header] = value
        return response

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    # Log all registered routes for debugging
    logger.info("Application routes registered", extra={
        'route_count': len(list(app.url_map.iter_rules())),
        'routes': [f"{rule} - {rule.methods}" for rule in app.url_map.iter_rules()]
    })

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
