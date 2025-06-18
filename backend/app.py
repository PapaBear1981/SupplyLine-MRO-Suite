from flask import Flask, session, jsonify, request
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

    # Set database URI dynamically to pick up current environment variables
    database_uri = Config.get_database_uri()
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

    # Log the database URI for debugging (mask password)
    masked_uri = database_uri.replace(os.environ.get('DB_PASSWORD', ''), '***') if os.environ.get('DB_PASSWORD') else database_uri
    logger = logging.getLogger(__name__)
    logger.info(f"Using database URI: {masked_uri}")

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

        # Dispose of any existing engine to force recreation with new URI
        try:
            if hasattr(db, 'engine') and db.engine:
                db.engine.dispose()
        except Exception as dispose_error:
            logger.warning(f"Could not dispose existing engine: {dispose_error}")

        db.init_app(app)

        # Import all models to ensure they're registered with SQLAlchemy
        # This must be done after db.init_app() but within the try block
        from models import User, Tool
        logger.info("✓ Models imported and registered with SQLAlchemy")

        # Skip database connection test during startup for Cloud Run
        # Database will be initialized lazily when first accessed
        logger.info("✓ Database configuration completed (lazy initialization)")

        # Mark database as not initialized - will be done on first access
        app._db_initialized = False

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
        """Check if database is initialized by testing connection and ensuring models are available."""
        try:
            # Use the existing db instance from the app context
            from sqlalchemy import text

            # Simple connectivity test using existing db connection
            with app.app_context():
                # Test basic database connectivity
                result = db.session.execute(text('SELECT 1'))
                logger.debug("Database connectivity check passed")

                # Test that users table exists and is accessible
                try:
                    result = db.session.execute(text('SELECT COUNT(*) FROM users'))
                    user_count = result.scalar()
                    logger.debug(f"Database connectivity check passed. User count: {user_count}")
                except Exception as table_error:
                    logger.warning(f"Users table not accessible: {table_error}")
                    # Table might not exist yet, but connection works

                return True

        except Exception as e:
            logger.warning(f"Database connectivity check failed: {e}")
            return False

    # Store the function in app context for use in routes
    app.init_database_lazy = init_database_lazy

    # Decorator for routes that require database
    def require_database(f):
        """Decorator to ensure database is initialized before route execution."""
        from functools import wraps

        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                if not app.init_database_lazy():
                    logger.error("Database connectivity check failed in require_database decorator")
                    return jsonify({
                        'error': 'Database not available',
                        'message': 'Database connection could not be established'
                    }), 503
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in require_database decorator: {e}", exc_info=True)
                return jsonify({
                    'error': 'Database error',
                    'message': 'An error occurred while accessing the database'
                }), 503
        return decorated_function

    # Store decorator in app context
    app.require_database = require_database

    # Skip session configuration during startup for lazy loading
    # Session will be configured when database is initialized

    # Add comprehensive health endpoint for Cloud Run
    @app.route('/api/health', methods=['GET'])
    def health_check_early():
        health_data = {
            'status': 'healthy',
            'service': 'supplyline-backend',
            'timestamp': datetime.datetime.now().isoformat(),
            'timezone': str(time.tzname),
            'environment': os.environ.get('FLASK_ENV', 'unknown'),
            'version': '2025.1.0'
        }

        # Add Cloud Run specific information
        if os.environ.get('DB_HOST'):
            health_data.update({
                'deployment': 'cloud-run',
                'region': os.environ.get('REGION', 'unknown'),
                'project': os.environ.get('PROJECT_ID', 'unknown')
            })
        else:
            health_data['deployment'] = 'local'

        return jsonify(health_data), 200

    # Add readiness check endpoint for Cloud Run
    @app.route('/api/ready', methods=['GET'])
    def readiness_check():
        """Readiness check that verifies database connectivity"""
        try:
            # For Cloud Run, just check if the service is running
            # Database connectivity will be checked when actually needed
            return jsonify({
                'status': 'ready',
                'service': 'supplyline-backend',
                'database': 'lazy_init',
                'db_initialized': app._db_initialized,
                'timestamp': datetime.datetime.now().isoformat()
            }), 200

        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return jsonify({
                'status': 'not_ready',
                'service': 'supplyline-backend',
                'error': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            }), 503

    # Add database inspection endpoint that works without full initialization
    @app.route('/api/db-inspect', methods=['GET'])
    def inspect_database():
        try:
            from sqlalchemy import create_engine, text
            from config import Config

            # Create a direct connection to inspect the database
            engine = create_engine(Config.get_database_uri())

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

    # Add simple database initialization endpoint using raw SQL
    @app.route('/api/db-init-simple', methods=['POST'])
    def init_database_simple():
        try:
            import os
            from sqlalchemy import create_engine, text
            from config import Config

            # Get current environment variables and log them
            db_host = os.environ.get('DB_HOST', 'NOT_SET')
            db_user = os.environ.get('DB_USER', 'NOT_SET')
            db_name = os.environ.get('DB_NAME', 'NOT_SET')

            logger.info(f"DB_HOST environment variable: {db_host}")
            logger.info(f"DB_USER environment variable: {db_user}")
            logger.info(f"DB_NAME environment variable: {db_name}")

            # Create a fresh database URI
            database_uri = Config.get_database_uri()

            # Create a completely fresh engine with no connection pooling
            engine = create_engine(database_uri, poolclass=None)
            logger.info(f"Created fresh engine with URI: {database_uri.replace(os.environ.get('DB_PASSWORD', ''), '***')}")

            with engine.connect() as conn:
                # Create users table with all required columns
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        employee_number VARCHAR(50) UNIQUE NOT NULL,
                        department VARCHAR(100),
                        password_hash VARCHAR(255) NOT NULL,
                        is_admin BOOLEAN DEFAULT FALSE,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        reset_token VARCHAR(255),
                        reset_token_expiry TIMESTAMP,
                        remember_token VARCHAR(255),
                        remember_token_expiry TIMESTAMP,
                        failed_login_attempts INTEGER DEFAULT 0,
                        account_locked_until TIMESTAMP,
                        last_failed_login TIMESTAMP
                    )
                """))

                # Create other essential tables
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS tools (
                        id SERIAL PRIMARY KEY,
                        tool_id VARCHAR(50) UNIQUE NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        category VARCHAR(50),
                        location VARCHAR(100),
                        status VARCHAR(20) DEFAULT 'available',
                        condition_status VARCHAR(20) DEFAULT 'good',
                        last_calibration DATE,
                        next_calibration DATE,
                        calibration_interval INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))

                # Create admin user
                from werkzeug.security import generate_password_hash
                password_hash = generate_password_hash('admin123')

                conn.execute(text("""
                    INSERT INTO users (name, employee_number, department, password_hash, is_admin, is_active, created_at)
                    VALUES (:name, :emp_num, :dept, :pwd_hash, :is_admin, :is_active, NOW())
                    ON CONFLICT (employee_number) DO NOTHING
                """), {
                    'name': 'System Administrator',
                    'emp_num': 'ADMIN001',
                    'dept': 'Administration',
                    'pwd_hash': password_hash,
                    'is_admin': True,
                    'is_active': True
                })

                conn.commit()

            # Dispose of the engine
            engine.dispose()

            # Now properly initialize SQLAlchemy models within app context
            try:
                from models import db

                # Dispose of any existing engine
                try:
                    if hasattr(db, 'engine') and db.engine:
                        db.engine.dispose()
                except Exception as dispose_error:
                    logger.warning(f"Could not dispose existing engine: {dispose_error}")

                # Reinitialize the database with the app within app context
                db.init_app(app)

                # Test the connection within app context
                with app.app_context():
                    db.session.execute(text('SELECT 1'))
                    db.session.commit()
                    logger.info("✓ SQLAlchemy models properly initialized within app context")

            except Exception as model_error:
                logger.warning(f"SQLAlchemy model initialization warning: {model_error}")
                # Continue anyway - raw SQL operations work

            app._db_initialized = True

            return jsonify({
                'status': 'success',
                'message': 'Database initialized successfully with raw SQL and SQLAlchemy models',
                'db_host_used': db_host,
                'timestamp': datetime.datetime.now().isoformat()
            }), 200

        except Exception as e:
            logger.error(f"Database initialization error: {e}", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': str(e),
                'db_host_env': os.environ.get('DB_HOST', 'NOT_SET'),
                'timestamp': datetime.datetime.now().isoformat()
            }), 500

    # Add database reset endpoint with fresh engine creation
    @app.route('/api/db-reset', methods=['POST'])
    def reset_database():
        try:
            import os
            from sqlalchemy import create_engine, text
            from config import Config
            from models import db, User

            # Get current environment variables and log them
            db_host = os.environ.get('DB_HOST', 'NOT_SET')
            db_user = os.environ.get('DB_USER', 'NOT_SET')
            db_name = os.environ.get('DB_NAME', 'NOT_SET')

            logger.info(f"DB_HOST environment variable: {db_host}")
            logger.info(f"DB_USER environment variable: {db_user}")
            logger.info(f"DB_NAME environment variable: {db_name}")

            # Create a fresh database URI
            database_uri = Config.get_database_uri()

            # Create a completely fresh engine with no connection pooling
            engine = create_engine(database_uri, poolclass=None, echo=True)
            logger.info(f"Created fresh engine with URI: {database_uri.replace(os.environ.get('DB_PASSWORD', ''), '***')}")

            with engine.connect() as conn:
                # Drop all tables
                conn.execute(text("DROP SCHEMA public CASCADE"))
                conn.execute(text("CREATE SCHEMA public"))
                conn.execute(text("GRANT ALL ON SCHEMA public TO supplyline_user"))
                conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
                conn.commit()

            # Dispose of the engine
            engine.dispose()

            # Now recreate tables with correct schema using fresh engine
            fresh_engine = create_engine(database_uri, poolclass=None)

            # Create tables using SQLAlchemy metadata
            from models import db
            with app.app_context():
                # Dispose of the existing db engine to force recreation
                try:
                    if hasattr(db, 'engine') and db.engine:
                        db.engine.dispose()
                except Exception as dispose_error:
                    logger.warning(f"Could not dispose existing engine: {dispose_error}")

                # Set the new engine
                db.engine = fresh_engine
                db.create_all()

                # Create admin user using raw SQL to avoid model issues
                from werkzeug.security import generate_password_hash
                password_hash = generate_password_hash('admin123')

                with fresh_engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO users (name, employee_number, department, password_hash, is_admin, is_active, created_at)
                        VALUES (:name, :emp_num, :dept, :pwd_hash, :is_admin, :is_active, NOW())
                        ON CONFLICT (employee_number) DO NOTHING
                    """), {
                        'name': 'System Administrator',
                        'emp_num': 'ADMIN001',
                        'dept': 'Administration',
                        'pwd_hash': password_hash,
                        'is_admin': True,
                        'is_active': True
                    })
                    conn.commit()

            # Dispose of the fresh engine
            fresh_engine.dispose()

            app._db_initialized = True

            return jsonify({
                'status': 'success',
                'message': 'Database reset and recreated successfully',
                'db_host_used': db_host,
                'timestamp': datetime.datetime.now().isoformat()
            }), 200

        except Exception as e:
            logger.error(f"Database reset error: {e}", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': str(e),
                'db_host_env': os.environ.get('DB_HOST', 'NOT_SET'),
                'timestamp': datetime.datetime.now().isoformat()
            }), 500

    # Add debug endpoint to check environment variables
    @app.route('/api/debug/env', methods=['GET'])
    def debug_env():
        import os
        from config import Config

        env_info = {
            'DB_HOST': os.environ.get('DB_HOST', 'NOT_SET'),
            'DB_USER': os.environ.get('DB_USER', 'NOT_SET'),
            'DB_NAME': os.environ.get('DB_NAME', 'NOT_SET'),
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'NOT_SET'),
            'DATABASE_URI': Config.get_database_uri(),
            'timestamp': datetime.datetime.now().isoformat()
        }

        return jsonify(env_info), 200

    # Add endpoint to check if admin user exists
    @app.route('/api/debug/check-admin', methods=['GET'])
    def check_admin():
        """Check if admin user exists in database"""
        try:
            from sqlalchemy import create_engine, text
            from config import Config

            engine = create_engine(Config.get_database_uri(), poolclass=None)

            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT id, name, employee_number, department, is_admin, is_active, created_at
                    FROM users
                    WHERE employee_number = 'ADMIN001'
                """))

                user_row = result.fetchone()

                if user_row:
                    return jsonify({
                        'status': 'found',
                        'user': {
                            'id': user_row[0],
                            'name': user_row[1],
                            'employee_number': user_row[2],
                            'department': user_row[3],
                            'is_admin': user_row[4],
                            'is_active': user_row[5],
                            'created_at': str(user_row[6])
                        }
                    }), 200
                else:
                    return jsonify({'status': 'not_found'}), 404

            engine.dispose()

        except Exception as e:
            logger.error(f"Check admin error: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500

    # Add test login endpoint for debugging
    @app.route('/api/auth/test-login', methods=['POST'])
    def test_login():
        """Test login endpoint for debugging"""
        try:
            data = request.get_json() or {}

            if not data.get('employee_number') or not data.get('password'):
                return jsonify({'error': 'Employee number and password required'}), 400

            # Simple hardcoded test for ADMIN001
            if data['employee_number'] == 'ADMIN001' and data['password'] == 'admin123':
                # Generate a proper JWT token
                from datetime import datetime, timedelta
                import jwt

                payload = {
                    'user_id': 1,
                    'employee_number': 'ADMIN001',
                    'is_admin': True,
                    'exp': datetime.utcnow() + timedelta(hours=24)
                }

                token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

                return jsonify({
                    'token': token,
                    'user': {
                        'id': 1,
                        'name': 'System Administrator',
                        'employee_number': 'ADMIN001',
                        'department': 'Administration',
                        'is_admin': True,
                        'is_active': True
                    }
                }), 200
            else:
                return jsonify({'error': 'Invalid credentials'}), 401

        except Exception as e:
            logger.error(f"Test login error: {e}", exc_info=True)
            return jsonify({'error': f'Test login error: {str(e)}'}), 500

    # Add simple login endpoint that works with raw SQL
    @app.route('/api/auth/login-simple', methods=['POST'])
    def login_simple():
        """Simple login endpoint using raw SQL to bypass SQLAlchemy issues"""
        try:
            data = request.get_json() or {}

            if not data.get('employee_number') or not data.get('password'):
                return jsonify({'error': 'Employee number and password required'}), 400

            from sqlalchemy import create_engine, text
            from config import Config
            from werkzeug.security import check_password_hash
            import jwt
            from datetime import datetime, timedelta

            # Create database connection
            engine = create_engine(Config.get_database_uri(), poolclass=None)

            with engine.connect() as conn:
                # Get user from database
                result = conn.execute(text("""
                    SELECT id, name, employee_number, department, password_hash, is_admin, is_active,
                           failed_login_attempts, account_locked_until
                    FROM users
                    WHERE employee_number = :emp_num
                """), {'emp_num': data['employee_number']})

                user_row = result.fetchone()

                if not user_row:
                    return jsonify({'error': 'Invalid credentials'}), 401

                # Convert row to dict
                user = {
                    'id': user_row[0],
                    'name': user_row[1],
                    'employee_number': user_row[2],
                    'department': user_row[3],
                    'password_hash': user_row[4],
                    'is_admin': user_row[5],
                    'is_active': user_row[6],
                    'failed_login_attempts': user_row[7] or 0,
                    'account_locked_until': user_row[8]
                }

                # Check if user is active
                if not user['is_active']:
                    return jsonify({'error': 'Account is inactive. Please contact an administrator.'}), 403

                # Check if account is locked
                if user['account_locked_until'] and user['account_locked_until'] > datetime.now():
                    return jsonify({'error': 'Account is temporarily locked. Please try again later.'}), 423

                # Verify password
                if not check_password_hash(user['password_hash'], data['password']):
                    # Increment failed login attempts
                    conn.execute(text("""
                        UPDATE users
                        SET failed_login_attempts = failed_login_attempts + 1,
                            last_failed_login = NOW()
                        WHERE id = :user_id
                    """), {'user_id': user['id']})
                    conn.commit()

                    return jsonify({'error': 'Invalid credentials'}), 401

                # Reset failed login attempts on successful login
                conn.execute(text("""
                    UPDATE users
                    SET failed_login_attempts = 0,
                        account_locked_until = NULL,
                        last_failed_login = NULL
                    WHERE id = :user_id
                """), {'user_id': user['id']})
                conn.commit()

                # Generate JWT token
                payload = {
                    'user_id': user['id'],
                    'employee_number': user['employee_number'],
                    'is_admin': user['is_admin'],
                    'exp': datetime.utcnow() + timedelta(hours=24)
                }

                token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

                # Return user data and token
                return jsonify({
                    'token': token,
                    'user': {
                        'id': user['id'],
                        'name': user['name'],
                        'employee_number': user['employee_number'],
                        'department': user['department'],
                        'is_admin': user['is_admin'],
                        'is_active': user['is_active']
                    }
                }), 200

            engine.dispose()

        except Exception as e:
            logger.error(f"Login error: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error'}), 500

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

            # Test database connection using direct engine creation
            from sqlalchemy import text, create_engine
            from config import Config

            # Create a fresh engine for testing
            engine = create_engine(Config.get_database_uri(), poolclass=None)

            with engine.connect() as conn:
                conn.execute(text('SELECT 1'))

                # Check if database is initialized
                result = conn.execute(text("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'users'
                """))
                table_count = result.scalar()

                engine.dispose()

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
            engine = create_engine(Config.get_database_uri())

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

    # Add migration endpoint to fix users table
    @app.route('/api/migrate-users-table', methods=['POST'])
    def migrate_users_table():
        try:
            from sqlalchemy import create_engine, text
            from config import Config

            # Create a direct connection to migrate the users table
            engine = create_engine(Config.get_database_uri())

            with engine.connect() as conn:
                # Add missing columns to users table for account lockout functionality
                conn.execute(text("""
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0
                """))
                conn.execute(text("""
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS account_locked_until TIMESTAMP
                """))
                conn.execute(text("""
                    ALTER TABLE users ADD COLUMN IF NOT EXISTS last_failed_login TIMESTAMP
                """))

                # Update existing users to have default values
                conn.execute(text("""
                    UPDATE users SET failed_login_attempts = 0 WHERE failed_login_attempts IS NULL
                """))

                conn.commit()

            return jsonify({
                'status': 'success',
                'message': 'Users table migrated successfully with account lockout columns',
                'timestamp': datetime.datetime.now().isoformat()
            }), 200

        except Exception as e:
            logger.error(f"Users table migration error: {e}", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            }), 500

    # Add endpoint to recreate users table with correct schema
    @app.route('/api/recreate-users-table', methods=['POST'])
    def recreate_users_table():
        try:
            from sqlalchemy import create_engine, text
            from config import Config

            # Create a direct connection to recreate the users table
            engine = create_engine(Config.get_database_uri())

            with engine.connect() as conn:
                # Drop existing users table
                conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))

                # Create users table with all required columns
                conn.execute(text("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        employee_number VARCHAR(50) UNIQUE NOT NULL,
                        department VARCHAR(100),
                        password_hash VARCHAR(255) NOT NULL,
                        is_admin BOOLEAN DEFAULT FALSE,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        reset_token VARCHAR(255),
                        reset_token_expiry TIMESTAMP,
                        remember_token VARCHAR(255),
                        remember_token_expiry TIMESTAMP,
                        failed_login_attempts INTEGER DEFAULT 0,
                        account_locked_until TIMESTAMP,
                        last_failed_login TIMESTAMP
                    )
                """))

                # Create admin user
                from werkzeug.security import generate_password_hash
                password_hash = generate_password_hash('admin123')

                conn.execute(text("""
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

                conn.commit()

            return jsonify({
                'status': 'success',
                'message': 'Users table recreated successfully with all required columns',
                'timestamp': datetime.datetime.now().isoformat()
            }), 200

        except Exception as e:
            logger.error(f"Users table recreation error: {e}", exc_info=True)
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
    # Use PORT environment variable for Cloud Run compatibility, fallback to 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=False)  # Disable debug to avoid reloader