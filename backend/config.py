import os
import logging.handlers
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration class"""

    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Fallback to SQLite for local development
        db_path = os.path.join(basedir, 'supplyline.db')
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database connection pooling and optimization
    @staticmethod
    def get_engine_options():
        database_url = os.environ.get('DATABASE_URL', 'sqlite:///supplyline.db')
        if database_url.startswith('postgresql'):
            # PostgreSQL specific options
            return {
                'echo': False,  # Set to True for SQL debugging
                'pool_pre_ping': True,  # Validate connections before use
                'pool_recycle': 3600,  # Recycle connections every hour
                'pool_size': 10,
                'max_overflow': 20
            }
        else:
            # SQLite and other databases
            return {
                'echo': False,  # Set to True for SQL debugging
            }

    SQLALCHEMY_ENGINE_OPTIONS = get_engine_options()

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 900))  # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 604800))  # 7 days

    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    CORS_SUPPORTS_CREDENTIALS = False  # JWT doesn't need credentials

    # Security Configuration
    BCRYPT_LOG_ROUNDS = int(os.environ.get('BCRYPT_LOG_ROUNDS', 12))

    # Import security configuration
    from security_config import SECURITY_HEADERS, CORS_CONFIG, RATE_LIMITS, PASSWORD_POLICY, ACCOUNT_LOCKOUT

    # Security headers
    SECURITY_HEADERS = SECURITY_HEADERS

    # Security policies
    ACCOUNT_LOCKOUT = ACCOUNT_LOCKOUT
    PASSWORD_POLICY = PASSWORD_POLICY
    RATE_LIMITS = RATE_LIMITS

    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')

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
                'level': LOG_LEVEL,
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
            'file': {
                'level': 'DEBUG',
                'formatter': 'json',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOG_FILE,
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            '': {
                'handlers': ['default', 'file'],
                'level': 'DEBUG',
                'propagate': False
            }
        }
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///supplyline_dev.db'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'echo': True,  # Enable SQL debugging in development
    }


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

    # Use PostgreSQL in production
    if not Config.DATABASE_URL:
        # Build PostgreSQL URL from individual components
        RDS_HOSTNAME = os.environ.get('RDS_HOSTNAME')
        RDS_PORT = os.environ.get('RDS_PORT', '5432')
        RDS_DB_NAME = os.environ.get('RDS_DB_NAME')
        RDS_USERNAME = os.environ.get('RDS_USERNAME')
        RDS_PASSWORD = os.environ.get('RDS_PASSWORD')

        if all([RDS_HOSTNAME, RDS_DB_NAME, RDS_USERNAME, RDS_PASSWORD]):
            SQLALCHEMY_DATABASE_URI = f'postgresql://{RDS_USERNAME}:{RDS_PASSWORD}@{RDS_HOSTNAME}:{RDS_PORT}/{RDS_DB_NAME}'

    # Enhanced security for production
    SECURITY_HEADERS = {
        **Config.SECURITY_HEADERS,
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload'
    }


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}  # Remove PostgreSQL-specific options
    JWT_ACCESS_TOKEN_EXPIRES = 60  # 1 minute for testing
    JWT_REFRESH_TOKEN_EXPIRES = 300  # 5 minutes for testing


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}