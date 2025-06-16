import os
import logging
import logging.handlers
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Use environment variables with fallbacks for local development
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # Database configuration - supports both SQLite (local) and PostgreSQL (Cloud SQL)
    @staticmethod
    def get_database_uri():
        # Check if we're in Cloud Run environment (Cloud SQL)
        if os.environ.get('DB_HOST') and os.environ.get('DB_USER'):
            # Cloud SQL PostgreSQL configuration
            db_user = os.environ.get('DB_USER')
            db_password = os.environ.get('DB_PASSWORD')
            db_name = os.environ.get('DB_NAME', 'supplyline')
            db_host = os.environ.get('DB_HOST')  # Unix socket path for Cloud SQL

            if db_host.startswith('/cloudsql/'):
                # Unix socket connection for Cloud SQL
                return f'postgresql+psycopg2://{db_user}:{db_password}@/{db_name}?host={db_host}'

            # TCP connection
            db_port = os.environ.get('DB_PORT', '5432')
            return f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        else:
            # SQLite for local development
            if os.path.exists('/database'):
                db_path = os.path.join('/database', 'tools.db')
            else:
                db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))
            logging.getLogger(__name__).debug(f"Using SQLite database path: {db_path}")
            return f'sqlite:///{db_path}'

    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database connection pooling and optimization
    @staticmethod
    def get_engine_options():
        if os.environ.get('DB_HOST'):
            # PostgreSQL/Cloud SQL configuration
            return {
                'echo': False,
                'pool_size': 5,
                'max_overflow': 10,
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'connect_args': {
                    'connect_timeout': 10,
                    'application_name': 'supplyline-mro-suite'
                }
            }

        # SQLite configuration
        return {
            'echo': False,
            'pool_pre_ping': True,
        }

    SQLALCHEMY_ENGINE_OPTIONS = get_engine_options()

    # Session configuration - Enhanced security
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)  # Shorter timeout for security

    # Session storage configuration - use database for cloud deployment
    @staticmethod
    def get_session_config():
        if os.environ.get('FLASK_ENV') == 'production' and os.environ.get('DB_HOST'):
            # Use database sessions for cloud deployment
            # Note: SESSION_SQLALCHEMY will be set in app.py after db is initialized
            return {
                'SESSION_TYPE': 'sqlalchemy',
                'SESSION_SQLALCHEMY_TABLE': 'sessions',
                'SESSION_PERMANENT': False,
                'SESSION_USE_SIGNER': True,
                'SESSION_KEY_PREFIX': 'supplyline:',
            }
        # Use filesystem sessions for local development
        if os.path.exists('/flask_session'):
            session_dir = '/flask_session'
        else:
            session_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'flask_session'))
        logging.getLogger(__name__).debug(f"Using session directory: {session_dir}")
        return {
            'SESSION_TYPE': 'filesystem',
            'SESSION_FILE_DIR': session_dir,
            'SESSION_PERMANENT': False,
            'SESSION_USE_SIGNER': True,
        }

    # Apply session configuration
    _session_config = get_session_config()
    SESSION_TYPE = _session_config['SESSION_TYPE']
    if 'SESSION_FILE_DIR' in _session_config:
        SESSION_FILE_DIR = _session_config['SESSION_FILE_DIR']
    if 'SESSION_SQLALCHEMY_TABLE' in _session_config:
        SESSION_SQLALCHEMY_TABLE = _session_config['SESSION_SQLALCHEMY_TABLE']
    SESSION_PERMANENT = _session_config['SESSION_PERMANENT']
    SESSION_USE_SIGNER = _session_config['SESSION_USE_SIGNER']
    if 'SESSION_KEY_PREFIX' in _session_config:
        SESSION_KEY_PREFIX = _session_config['SESSION_KEY_PREFIX']

    # Session cleanup configuration
    SESSION_CLEANUP_INTERVAL = 3600  # 1 hour
    SESSION_MAX_AGE = 86400  # 24 hours

    # Enhanced cookie settings - secure for production
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'  # HTTPS only in production
    SESSION_COOKIE_HTTPONLY = True  # Prevent XSS

    # Structured logging configuration
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d'
            },
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            }
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
            'file': {
                'level': 'DEBUG',
                'formatter': 'json',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'app.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'error_file': {
                'level': 'ERROR',
                'formatter': 'json',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'error.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 10
            }
        },
        'loggers': {
            '': {
                'handlers': ['default', 'file', 'error_file'],
                'level': 'DEBUG',
                'propagate': False
            }
        }
    }

    # Resource monitoring thresholds
    RESOURCE_THRESHOLDS = {
        'memory_percent': 80,
        'disk_percent': 85,
        'open_files': 1000,
        'db_connections': 8  # 80% of pool size
    }
    SESSION_COOKIE_SAMESITE = 'Lax'  # Allow cross-site requests for mobile
    SESSION_COOKIE_NAME = 'supplyline_session'  # Custom name

    # Session security options
    SESSION_VALIDATE_IP = os.environ.get('SESSION_VALIDATE_IP', 'false').lower() == 'true'

    # CORS settings - environment-specific
    @staticmethod
    def get_cors_origins():
        cors_origins = os.environ.get('CORS_ORIGINS')
        if cors_origins:
            return cors_origins.split(',')
        elif os.environ.get('FLASK_ENV') == 'production':
            # Production default - should be overridden by environment variable
            return ['https://supplyline-frontend-*.a.run.app']
        else:
            # Development defaults
            return [
                'http://localhost:5173',
                'http://localhost:5174',  # Added for current frontend dev server
                'http://127.0.0.1:5173',
                'http://127.0.0.1:5174',  # Added for current frontend dev server
                'http://192.168.1.122:5173',
                'http://100.108.111.69:5173'
            ]

    CORS_ORIGINS = get_cors_origins()
    CORS_SUPPORTS_CREDENTIALS = True

    # Additional security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }

    # Account lockout settings
    ACCOUNT_LOCKOUT = {
        'MAX_FAILED_ATTEMPTS': int(os.environ.get('MAX_FAILED_ATTEMPTS', 5)),  # Number of failed attempts before account is locked
        'INITIAL_LOCKOUT_MINUTES': int(os.environ.get('INITIAL_LOCKOUT_MINUTES', 15)),  # Initial lockout duration in minutes
        'LOCKOUT_MULTIPLIER': int(os.environ.get('LOCKOUT_MULTIPLIER', 2)),  # Multiplier for subsequent lockouts
        'MAX_LOCKOUT_MINUTES': int(os.environ.get('MAX_LOCKOUT_MINUTES', 60))  # Maximum lockout duration in minutes
    }