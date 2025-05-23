import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Use environment variables with fallbacks for local development
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # SQLite database path - using absolute path from project root
    # Check if we're in Docker environment (look for /database volume)
    if os.path.exists('/database'):
        db_path = os.path.join('/database', 'tools.db')
    else:
        db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))
    print(f"Using database path: {db_path}")
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session configuration - Enhanced security
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)  # Shorter timeout for security
    SESSION_TYPE = 'filesystem'
    # Check if we're in Docker environment (look for /flask_session volume)
    if os.path.exists('/flask_session'):
        SESSION_FILE_DIR = '/flask_session'
    else:
        SESSION_FILE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'flask_session'))
    print(f"Using session directory: {SESSION_FILE_DIR}")

    # Enhanced cookie settings
    SESSION_COOKIE_SECURE = True  # Always use HTTPS in production
    SESSION_COOKIE_HTTPONLY = True  # Prevent XSS
    SESSION_COOKIE_SAMESITE = 'Strict'  # Prevent CSRF
    SESSION_USE_SIGNER = True  # Sign cookies
    SESSION_COOKIE_NAME = 'supplyline_session'  # Custom name

    # Session security options
    SESSION_VALIDATE_IP = os.environ.get('SESSION_VALIDATE_IP', 'false').lower() == 'true'

    # CORS settings - more restrictive in production
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
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