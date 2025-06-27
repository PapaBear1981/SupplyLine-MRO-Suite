from flask import Flask, session, jsonify
from routes import register_routes
from config import Config
from flask_session import Session
from flask_cors import CORS
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
    supports_credentials = app.config.get('CORS_SUPPORTS_CREDENTIALS', False)

    logger = logging.getLogger(__name__)
    logger.info(f"CORS configured with origins: {allowed_origins}, credentials: {supports_credentials}")

    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-CSRF-Token", "X-Requested-With"],
            "supports_credentials": supports_credentials
        }
    })

    # Initialize Flask-Session
    Session(app)

    # Initialize session cleanup
    init_session_cleanup(app)

    # Initialize resource monitoring
    init_resource_monitoring(app)

    # Setup request logging middleware
    setup_request_logging(app)

    # Get logger after logging is configured
    logger = logging.getLogger(__name__)

    # Log current time information for debugging
    logger.info("Application starting", extra={
        'utc_time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'local_time': datetime.datetime.now().isoformat()
    })

    # Initialize database if needed (AWS deployment support)
    with app.app_context():
        try:
            # Import database models
            from models import db

            # Set engine options dynamically
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = Config.get_engine_options()

            # Check if database needs initialization
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            if not tables:
                logger.info("No database tables found. Initializing database...")

                # For AWS deployment, use the comprehensive initialization script
                if os.environ.get('DB_HOST'):
                    logger.info("AWS environment detected. Running comprehensive database initialization...")
                    try:
                        from aws_db_init import initialize_aws_database
                        success = initialize_aws_database()
                        if success:
                            logger.info("AWS database initialization completed successfully")
                        else:
                            logger.error("AWS database initialization failed")
                            raise Exception("AWS database initialization failed")
                    except ImportError:
                        logger.warning("AWS database initialization script not found, falling back to basic initialization")
                        db.create_all()
                        logger.info("Database tables created successfully")

                        # Create admin user securely
                        from utils.admin_init import create_secure_admin
                        success, message, password = create_secure_admin()
                        if success:
                            logger.info(f"Admin creation: {message}")
                            if password:
                                logger.warning("IMPORTANT: Generated admin password")
                                logger.warning(f"Username: ADMIN001")
                                logger.warning(f"Password: {password}")
                                logger.warning("Please change the password after first login!")
                        else:
                            logger.error(f"Admin creation failed: {message}")
                else:
                    # Local development initialization
                    logger.info("Local environment detected. Creating basic database structure...")
                    db.create_all()
                    logger.info("Database tables created successfully")

                    # Create admin user securely
                    from utils.admin_init import create_secure_admin
                    success, message, password = create_secure_admin()
                    if success:
                        logger.info(f"Admin creation: {message}")
                        if password:
                            logger.warning("IMPORTANT: Generated admin password")
                            logger.warning(f"Username: ADMIN001")
                            logger.warning(f"Password: {password}")
                            logger.warning("Please change the password after first login!")
                    else:
                        logger.error(f"Admin creation failed: {message}")
            else:
                logger.info(f"Database tables already exist: {len(tables)} tables found")

        except Exception as e:
            logger.error("Database initialization failed", exc_info=True, extra={
                'error_message': str(e)
            })
            # Don't abort startup for database initialization issues in development
            if os.environ.get('DB_HOST'):
                raise  # Abort in production if database initialization fails

    # Run database migrations
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
        logger.error("Performance indexes migration failed – aborting startup", exc_info=True, extra={
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

    # Register JWT authentication routes first
    from routes_auth import register_auth_routes
    register_auth_routes(app)

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