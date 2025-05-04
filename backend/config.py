import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Use environment variables with fallbacks for local development
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # SQLite database file in project root under database/
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join('/app/database', 'tools.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = '/app/flask_session'

    # Cookie settings - adjust based on environment
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'  # True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_USE_SIGNER = True

    # CORS settings - more restrictive in production
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
    CORS_SUPPORTS_CREDENTIALS = True