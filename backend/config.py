import os
import logging.handlers
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Use environment variables with fallbacks for local development
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # Database configuration - supports both SQLite (local) and PostgreSQL (AWS)
    @staticmethod
    def get_database_uri():
        """Get database URI based on environment"""
        # Check for PostgreSQL environment variables (AWS deployment)
        db_host = os.environ.get('DB_HOST')
        db_port = os.environ.get('DB_PORT', '5432')
        db_name = os.environ.get('DB_NAME', 'supplyline')
        db_user = os.environ.get('DB_USER', 'supplyline_admin')
        db_password = os.environ.get('DB_PASSWORD')

        if db_host and db_password:
            # PostgreSQL for AWS deployment
            print(f"Using PostgreSQL database: {db_host}:{db_port}/{db_name}")
            return f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        else:
            # SQLite for local development
            if os.path.exists('/database'):
                db_path = os.path.join('/database', 'tools.db')
            else:
                db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))
            print(f"Using SQLite database: {db_path}")
            return f'sqlite:///{db_path}'

    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database connection pooling and optimization
    @staticmethod
    def get_engine_options():
        """Get database engine options based on database type"""
        # Get the database URI using the same method
        db_uri = Config.get_database_uri()
        if 'postgresql' in db_uri:
            # PostgreSQL configuration
            return {
                'echo': False,
                'pool_size': 10,
                'max_overflow': 20,
                'pool_pre_ping': True,
                'pool_recycle': 3600,  # Recycle connections every hour
                'connect_args': {
                    'connect_timeout': 30,
                    'application_name': 'SupplyLine-MRO-Suite'
                }
            }
        else:
            # SQLite configuration
            return {
                'echo': False,
                'pool_pre_ping': True,
            }

    # SQLALCHEMY_ENGINE_OPTIONS will be set dynamically in app.py

    # Session configuration - Enhanced security
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)  # Shorter timeout for security
    SESSION_TYPE = 'filesystem'
    # Check if we're in Docker environment (look for /flask_session volume)
    if os.path.exists('/flask_session'):
        SESSION_FILE_DIR = '/flask_session'
    else:
        SESSION_FILE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'flask_session'))
    print(f"Using session directory: {SESSION_FILE_DIR}")

    # Session cleanup configuration
    SESSION_CLEANUP_INTERVAL = 3600  # 1 hour
    SESSION_MAX_AGE = 86400  # 24 hours

    # Enhanced cookie settings
    SESSION_COOKIE_SECURE = False  # Set to True only in HTTPS production
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
    SESSION_USE_SIGNER = True  # Sign cookies
    SESSION_COOKIE_NAME = 'supplyline_session'  # Custom name

    # Session security options
    SESSION_VALIDATE_IP = os.environ.get('SESSION_VALIDATE_IP', 'false').lower() == 'true'

    # CORS settings - more restrictive in production
    # Default includes both development (5173) and Docker (80) ports
    default_origins = 'http://localhost:5173,http://127.0.0.1:5173,http://localhost:80,http://127.0.0.1:80,http://localhost,http://127.0.0.1'
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', default_origins).split(',')
    CORS_SUPPORTS_CREDENTIALS = False  # JWT doesn't need credentials

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