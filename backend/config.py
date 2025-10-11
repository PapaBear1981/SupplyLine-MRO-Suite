import os
import logging.handlers
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Security: Require SECRET_KEY and JWT_SECRET_KEY to be set via environment variables
    # This prevents the use of hardcoded default values in production
    # Exception: Testing environment can set these via app.config after initialization

    # Load from environment variables (may be None if not set)
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

    # Database configuration - check for DATABASE_URL environment variable first
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        print(f"Using PostgreSQL database from DATABASE_URL")
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Fallback to SQLite database path - using absolute path from project root
        # Check if we're in Docker environment (look for /database volume)
        if os.path.exists('/database'):
            db_path = os.path.join('/database', 'tools.db')
        else:
            db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))
        print(f"Using SQLite database path: {db_path}")
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database connection pooling and optimization
    if DATABASE_URL:
        # PostgreSQL connection pooling options
        SQLALCHEMY_ENGINE_OPTIONS = {
            'echo': False,  # Set to True for SQL debugging
            'pool_pre_ping': True,  # Validate connections before use
            'pool_size': 10,  # Number of connections to maintain
            'max_overflow': 20,  # Additional connections beyond pool_size
            'pool_timeout': 30,  # Timeout for getting connection from pool
            'pool_recycle': 3600,  # Recycle connections after 1 hour
        }
    else:
        # SQLite doesn't support connection pooling, so we only set basic options
        SQLALCHEMY_ENGINE_OPTIONS = {
            'echo': False,  # Set to True for SQL debugging
            'pool_pre_ping': True,  # Validate connections before use
        }

    # Session configuration - Enhanced security
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)  # Shorter timeout for security

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

    # CORS settings - more restrictive in production
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173,http://192.168.1.122:5173,http://100.108.111.69:5173').split(',')
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'X-CSRF-Token']
    CORS_SUPPORTS_CREDENTIALS = False

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

    @staticmethod
    def validate_security_config(app_config):
        """
        Validate that required security configuration is present.
        This is called after app initialization to allow test fixtures to set values programmatically.

        Args:
            app_config: Flask app.config object

        Raises:
            RuntimeError: If required security keys are missing in non-testing environments
        """
        # Check if we're in testing mode
        is_testing = os.environ.get('FLASK_ENV') == 'testing' or app_config.get('TESTING', False)

        if not is_testing:
            if not app_config.get('SECRET_KEY'):
                raise RuntimeError(
                    'SECRET_KEY must be set in production. '
                    'Set the SECRET_KEY environment variable or app.config["SECRET_KEY"]. '
                    'Generate a secure key using: python -c "import secrets; print(secrets.token_urlsafe(64))"'
                )

            if not app_config.get('JWT_SECRET_KEY'):
                raise RuntimeError(
                    'JWT_SECRET_KEY must be set in production. '
                    'Set the JWT_SECRET_KEY environment variable or app.config["JWT_SECRET_KEY"]. '
                    'Generate a secure key using: python -c "import secrets; print(secrets.token_urlsafe(64))"'
                )