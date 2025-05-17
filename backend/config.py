import os
import secrets
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Use environment variables with fallbacks for local development
    # Generate a secure random key if not provided
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))

    # SQLite database path - using absolute path from project root
    # Check if we're in Docker environment (look for /database volume)
    if os.path.exists('/database'):
        db_path = os.path.join('/database', 'tools.db')
    else:
        db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))
    print(f"Using database path: {db_path}")
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Prevent SQL injection by disabling SQLAlchemy event system
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'check_same_thread': False}
    }

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_TYPE = 'filesystem'
    # Check if we're in Docker environment (look for /flask_session volume)
    if os.path.exists('/flask_session'):
        SESSION_FILE_DIR = '/flask_session'
    else:
        SESSION_FILE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'flask_session'))
    print(f"Using session directory: {SESSION_FILE_DIR}")

    # Cookie settings - adjust based on environment
    # In production, always use secure cookies
    is_production = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_SECURE = is_production  # True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_USE_SIGNER = True

    # Set session timeout
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)  # Shorter session lifetime for security

    # CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('CSRF_SECRET_KEY', secrets.token_hex(32))

    # Content Security Policy
    CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'script-src': "'self'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data:",
        'font-src': "'self'",
        'connect-src': "'self'"
    }

    # CORS settings - more restrictive in production
    if is_production:
        # In production, only allow specific origins
        CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    else:
        # In development, allow common local development servers
        CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')

    CORS_SUPPORTS_CREDENTIALS = True

    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains' if is_production else None,
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'