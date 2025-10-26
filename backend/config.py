import os
import secrets
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
        print("Using PostgreSQL database from DATABASE_URL")
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Fallback to SQLite database path - using absolute path from project root
        # Check if we're in Docker environment (look for /database volume)
        if os.path.exists('/database'):
            db_path = os.path.join('/database', 'tools.db')
        else:
            db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))

        # Ensure the database directory exists
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"Created database directory: {db_dir}")

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

    # Cookie security settings
    # SECURITY: Set to True in production to require HTTPS for cookies
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() in ('true', '1', 'yes')
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookies
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection

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

    # PERFORMANCE & RESILIENCE: Request size and timeout limits
    # Maximum request body size (16 MB default, configurable via environment)
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB

    # Bulk import specific limits
    MAX_BULK_IMPORT_FILE_SIZE = int(os.environ.get('MAX_BULK_IMPORT_FILE_SIZE', 10 * 1024 * 1024))  # 10 MB
    MAX_BULK_IMPORT_ROWS = int(os.environ.get('MAX_BULK_IMPORT_ROWS', 10000))  # Maximum rows per import
    BULK_IMPORT_TIMEOUT = int(os.environ.get('BULK_IMPORT_TIMEOUT', 300))  # 5 minutes timeout

    # Request timeout for long-running operations (seconds)
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 60))  # 60 seconds default

    # Public URL for QR codes - should be accessible from external devices
    # Set this to your server's network IP or domain name
    # Example: http://192.168.1.100:5000 or https://yourdomain.com
    PUBLIC_URL = os.environ.get('PUBLIC_URL', None)

    # CORS settings - SECURITY: Never use wildcard (*) origins in production
    # Only allow specific, trusted origins. Update CORS_ORIGINS environment variable
    # to include your production frontend URL(s)
    cors_origins_str = os.environ.get('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173')
    CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(',') if origin.strip() and origin.strip() != '*']

    # Validate that wildcard is not used
    if '*' in CORS_ORIGINS or not CORS_ORIGINS:
        raise ValueError(
            'CORS_ORIGINS must not contain wildcard (*) and must have at least one valid origin. '
            'Set specific origins via CORS_ORIGINS environment variable (comma-separated).'
        )

    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'X-CSRF-Token']
    CORS_SUPPORTS_CREDENTIALS = True  # Required for HttpOnly cookies to work with CORS

    # Additional security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosnif',
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

        if is_testing:
            return

        # Determine runtime environment context
        env_value = (
            app_config.get('ENV')
            or os.environ.get('FLASK_ENV')
            or os.environ.get('ENVIRONMENT')
            or ''
        ).strip().lower()
        truthy_ci_values = {'true', '1', 'yes', 'on'}
        is_ci = (
            os.environ.get('CI', '').strip().lower() in truthy_ci_values
            or os.environ.get('GITHUB_ACTIONS', '').strip().lower() in truthy_ci_values
        )
        is_development = (
            env_value in {'development', 'dev'}
            or bool(app_config.get('DEBUG'))
        )
        env_label = f"{env_value} environment" if env_value else "the current environment"

        def _ensure_key(config_key: str, description: str) -> None:
            key_value = app_config.get(config_key)
            if key_value is not None and key_value != '':
                return

            if is_ci or is_development:
                generated_key = secrets.token_urlsafe(64)
                app_config[config_key] = generated_key
                print(
                    f"Generated ephemeral {description} for CI/development environment. "
                    "Set an explicit value via environment variables for non-development deployments."
                )
                return

            raise RuntimeError(
                f"{config_key} must be set for {env_label} when running outside CI or development. "
                f'Set the {config_key} environment variable or app.config["{config_key}"]. '
                'Generate a secure key using: python -c "import secrets; print(secrets.token_urlsafe(64))"'
            )

        _ensure_key('SECRET_KEY', 'Flask SECRET_KEY')
        _ensure_key('JWT_SECRET_KEY', 'JWT secret key')
