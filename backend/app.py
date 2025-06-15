from flask import Flask, session, jsonify
from backend.routes import register_routes
from config import Config
from flask_session import Session
from flask_cors import CORS
import os
import sys
import time
import datetime
import logging.config
from utils.session_cleanup import init_session_cleanup
# Resource monitoring import moved to conditional block
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
    # Apply CORS to all routes so that error responses (e.g. 404) also include
    # the necessary headers.  Previously CORS was limited to the ``/api``
    # prefix which meant requests to undefined routes would omit the
    # ``Access-Control-Allow-Origin`` header, causing the frontend to report a
    # CORS error.  Expanding the resource pattern ensures the middleware runs
    # for every request path.
    CORS(app, resources={
        r"/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-CSRF-Token"],
            "supports_credentials": True,
        }
    })

    # Initialize database first
    from backend.models import db
    db.init_app(app)

    # Configure SESSION_SQLALCHEMY for database sessions if needed
    if app.config.get('SESSION_TYPE') == 'sqlalchemy':
        app.config['SESSION_SQLALCHEMY'] = db

    # Add health endpoint before session initialization to avoid session issues
    @app.route('/api/health', methods=['GET'])
    def health_check_early():
        try:
            # Test database connection
            from sqlalchemy import text
            from backend.models import db
            with db.engine.connect() as conn:
                conn.execute(text('SELECT 1'))

            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.datetime.now().isoformat(),
                'timezone': str(time.tzname)
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': 'database_unavailable',
                'timestamp': datetime.datetime.now().isoformat()
            }), 503

    # Initialize Flask-Session
    Session(app)

    # Initialize session cleanup
    init_session_cleanup(app)

    # Setup request logging middleware
    setup_request_logging(app)

    # Get logger after logging is configured
    logger = logging.getLogger(__name__)

    # Initialize resource monitoring (only for local development)
    # Skip resource monitoring for Cloud Run/containerized deployments
    if not os.environ.get('DB_HOST'):  # Only run for local development
        try:
            from utils.resource_monitor import init_resource_monitoring
            init_resource_monitoring(app)
            logger.info("Resource monitoring initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize resource monitoring", exc_info=True)
    else:
        logger.info("Skipping resource monitoring for Cloud Run deployment")

    # Log current time information for debugging
    logger.info("Application starting", extra={
        'utc_time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'local_time': datetime.datetime.now().isoformat()
    })

    # Run database migrations (only for SQLite/local development)
    # Skip migrations for PostgreSQL/Cloud SQL deployments
    if not os.environ.get('DB_HOST'):  # Only run for local SQLite
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
    else:
        logger.info("Skipping SQLite migrations for PostgreSQL/Cloud SQL deployment")

    # Setup global error handlers
    from utils.error_handler import setup_global_error_handlers
    setup_global_error_handlers(app)

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