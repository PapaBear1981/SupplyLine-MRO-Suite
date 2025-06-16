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
# from utils.session_cleanup import init_session_cleanup  # Disabled for now
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

    # Session cookie name is already set in config.py - no need to set it again

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
    print(f"DEBUG: CORS allowed origins: {allowed_origins}")  # Debug output
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

    # Get logger early for use throughout the function
    logger = logging.getLogger(__name__)

    # Initialize database during app creation with error handling
    logger.info("Initializing database connection")

    try:
        from models import db, User
        db.init_app(app)

        # Test database connection and create tables if needed
        with app.app_context():
            # Test connection first
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            logger.info("✓ Database connection successful")

            # Create tables
            db.create_all()
            logger.info("✓ Database tables created/verified")

            # For Cloud SQL, check if admin user exists using raw SQL to avoid model issues
            if os.environ.get('DB_HOST'):
                try:
                    # Check if admin user exists using raw SQL
                    result = db.session.execute(text("SELECT COUNT(*) FROM users WHERE employee_number = 'ADMIN001'"))
                    admin_count = result.scalar()

                    if admin_count == 0:
                        # Create admin user using raw SQL to avoid model issues during startup
                        from werkzeug.security import generate_password_hash
                        password_hash = generate_password_hash('admin123')
                        db.session.execute(text("""
                            INSERT INTO users (name, employee_number, department, password_hash, is_admin, is_active, created_at)
                            VALUES (:name, :emp_num, :dept, :pwd_hash, :is_admin, :is_active, NOW())
                        """), {
                            'name': 'System Administrator',
                            'emp_num': 'ADMIN001',
                            'dept': 'Administration',
                            'pwd_hash': password_hash,
                            'is_admin': True,
                            'is_active': True
                        })
                        db.session.commit()
                        logger.info("✓ Admin user created")
                    else:
                        logger.info("✓ Admin user already exists")
                except Exception as e:
                    logger.warning(f"Could not verify/create admin user during startup: {e}")
                    # Continue without failing - admin user can be created later via API

        app._db_initialized = True
        logger.info("✓ Database initialization completed successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        app._db_initialized = False

        # For Cloud SQL, we'll continue without database and let routes handle the error
        if os.environ.get('DB_HOST'):
            logger.warning("Continuing without database - routes will return appropriate errors")
        else:
            # For local development, this is a critical error
            raise

    # Database initialization function for routes
    def init_database_lazy():
        """Check if database is initialized."""
        return app._db_initialized

    # Store the function in app context for use in routes
    app.init_database_lazy = init_database_lazy

    # Decorator for routes that require database
    def require_database(f):
        """Decorator to ensure database is initialized before route execution."""
        from functools import wraps

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not app.init_database_lazy():
                return jsonify({
                    'error': 'Database not available',
                    'message': 'Database connection could not be established'
                }), 503
            return f(*args, **kwargs)
        return decorated_function

    # Store decorator in app context
    app.require_database = require_database

    # Skip session configuration during startup for lazy loading
    # Session will be configured when database is initialized

    # Add simple health endpoint that doesn't require database
    @app.route('/api/health', methods=['GET'])
    def health_check_early():
        return jsonify({
            'status': 'healthy',
            'service': 'supplyline-backend',
            'timestamp': datetime.datetime.now().isoformat(),
            'timezone': str(time.tzname)
        }), 200

    # Add database inspection endpoint that works without full initialization
    @app.route('/api/db-inspect', methods=['GET'])
    def inspect_database():
        try:
            from sqlalchemy import create_engine, text
            from config import Config

            # Create a direct connection to inspect the database
            engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

            with engine.connect() as conn:
                # List all tables
                result = conn.execute(text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
                tables = [row[0] for row in result]

                # Get users table structure if it exists
                users_columns = []
                if 'users' in tables:
                    result = conn.execute(text("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_schema = 'public' AND table_name = 'users'
                        ORDER BY ordinal_position
                    """))
                    users_columns = [{'name': row[0], 'type': row[1], 'nullable': row[2]} for row in result]

                return jsonify({
                    'status': 'success',
                    'tables': tables,
                    'users_table_columns': users_columns,
                    'db_initialized': app._db_initialized,
                    'timestamp': datetime.datetime.now().isoformat()
                }), 200

        except Exception as e:
            logger.error(f"Database inspection error: {e}", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            }), 500

    # Add database reset endpoint
    @app.route('/api/db-reset', methods=['POST'])
    def reset_database():
        try:
            from sqlalchemy import create_engine, text
            from config import Config
            from models import db, User

            # Create a direct connection to reset the database
            engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

            with engine.connect() as conn:
                # Drop all tables
                conn.execute(text("DROP SCHEMA public CASCADE"))
                conn.execute(text("CREATE SCHEMA public"))
                conn.execute(text("GRANT ALL ON SCHEMA public TO supplyline_user"))
                conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
                conn.commit()

            # Now recreate tables with correct schema
            with app.app_context():
                db.create_all()

                # Create admin user
                admin_user = User(
                    name='System Administrator',
                    employee_number='ADMIN001',
                    department='Administration',
                    is_admin=True,
                    is_active=True
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()

            app._db_initialized = True

            return jsonify({
                'status': 'success',
                'message': 'Database reset and recreated successfully',
                'timestamp': datetime.datetime.now().isoformat()
            }), 200

        except Exception as e:
            logger.error(f"Database reset error: {e}", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            }), 500

    # Add database initialization endpoint with lazy loading
    @app.route('/api/init-db', methods=['POST'])
    def init_database():
        try:
            # Initialize database lazily (this will create tables and admin user)
            if not app.init_database_lazy():
                return jsonify({
                    'status': 'error',
                    'message': 'Database initialization failed',
                    'timestamp': datetime.datetime.now().isoformat()
                }), 500

            # Test database connection
            from sqlalchemy import text
            from models import db
            with db.engine.connect() as conn:
                conn.execute(text('SELECT 1'))

                # Check if database is initialized
                result = conn.execute(text("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'users'
                """))
                table_count = result.scalar()

                return jsonify({
                    'status': 'success',
                    'message': 'Database connection and initialization successful',
                    'tables_found': table_count > 0,
                    'table_count': int(table_count),
                    'timestamp': datetime.datetime.now().isoformat()
                }), 200

        except Exception as e:
            logger.error(f"Database initialization error: {e}", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': 'Database initialization failed',
                'error': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            }), 500

    # Add session table creation endpoint
    @app.route('/api/create-sessions-table', methods=['POST'])
    def create_sessions_table():
        try:
            from sqlalchemy import create_engine, text
            from config import Config

            # Create a direct connection to create the sessions table
            engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

            with engine.connect() as conn:
                # Create sessions table for Flask-Session
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id SERIAL PRIMARY KEY,
                        session_id VARCHAR(255) UNIQUE NOT NULL,
                        data BYTEA,
                        expiry TIMESTAMP
                    )
                """))
                conn.commit()

            return jsonify({
                'status': 'success',
                'message': 'Sessions table created successfully',
                'timestamp': datetime.datetime.now().isoformat()
            }), 200

        except Exception as e:
            logger.error(f"Sessions table creation error: {e}", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            }), 500

    # Skip Flask-Session initialization for now to avoid startup issues
    # Use default Flask sessions instead
    logger.info("Using default Flask sessions for simplicity")

    # Setup request logging middleware
    setup_request_logging(app)

    # Skip resource monitoring for all deployments to avoid startup issues
    logger.info("Skipping resource monitoring to ensure reliable startup")

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

    # Skip all migrations for Cloud SQL deployments to avoid startup issues
    if not os.environ.get('DB_HOST'):  # Only run for local SQLite
        logger.info("Local SQLite deployment detected - migrations will be run on first database access")
        # Note: Migration imports moved to lazy loading to avoid startup issues
    else:
        logger.info("PostgreSQL/Cloud SQL deployment detected - skipping migrations, database initialization available via /api/init-db endpoint")

    # Setup global error handlers with fallback
    try:
        from utils.error_handler import setup_global_error_handlers
        setup_global_error_handlers(app)
        logger.info("Global error handlers configured successfully")
    except Exception as e:
        logger.error(f"Failed to setup global error handlers: {e}")
        # Add basic error handlers as fallback
        @app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Resource not found'}), 404

        @app.errorhandler(500)
        def internal_error(error):
            return jsonify({'error': 'Internal server error'}), 500

    # Register main routes with error handling
    try:
        register_routes(app)
        logger.info("Routes registered successfully")
    except Exception as e:
        logger.error(f"Failed to register routes: {e}", exc_info=True)
        # Add minimal health endpoint as fallback
        @app.route('/api/health', methods=['GET'])
        def fallback_health():
            return jsonify({
                'status': 'degraded',
                'service': 'supplyline-backend',
                'error': 'Routes registration failed'
            }), 200

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
    app.run(host="0.0.0.0", port=5000, debug=False)  # Disable debug to avoid reloader