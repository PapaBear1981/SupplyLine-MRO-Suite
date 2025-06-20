from flask import Flask, jsonify
from routes import register_routes
from routes_auth import register_auth_routes
from config import config
from flask_cors import CORS
import os
import sys
import time
import datetime
import logging.config

def create_app(config_name=None):
    """Create Flask application with specified configuration"""

    # Set the system timezone to UTC
    os.environ['TZ'] = 'UTC'
    try:
        time.tzset()
        print("System timezone set to UTC")  # Keep this as print since logging not yet configured
    except AttributeError:
        # Windows doesn't have time.tzset()
        print("Running on Windows, cannot set system timezone. Ensure system time is correct.")

    # Create Flask app
    app = Flask(__name__, instance_relative_config=False)

    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])

    # Configure structured logging
    if hasattr(app.config, 'LOGGING_CONFIG'):
        try:
            logging.config.dictConfig(app.config['LOGGING_CONFIG'])
            logging.getLogger(__name__).info("Structured logging configured successfully")
        except Exception as e:
            logging.getLogger(__name__).warning("Error configuring logging: %s", e)
            # Fall back to basic logging
            logging.basicConfig(level=logging.INFO)

    # Initialize CORS with settings from config
    allowed_origins = app.config.get('CORS_ORIGINS', ['http://localhost:5173'])
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": app.config.get('CORS_SUPPORTS_CREDENTIALS', False)
        }
    })

    # Initialize database
    from models import db
    db.init_app(app)

    # Setup security middleware
    from security import setup_security_middleware
    setup_security_middleware(app)

    # Get logger after logging is configured
    logger = logging.getLogger(__name__)

    # Log current time information for debugging
    logger.info("Application starting", extra={
        'utc_time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'local_time': datetime.datetime.now().isoformat()
    })

    # Create database tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise

    # Register authentication routes
    register_auth_routes(app)

    # Register main routes
    register_routes(app)

    # Add security headers middleware
    @app.after_request
    def add_security_headers(response):
        security_headers = app.config.get('SECURITY_HEADERS', {})
        for header, value in security_headers.items():
            response.headers[header] = value
        return response

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'timestamp': datetime.datetime.utcnow().isoformat()})

    # Log all registered routes for debugging
    logger.info("Application routes registered", extra={
        'route_count': len(list(app.url_map.iter_rules())),
        'routes': [f"{rule} - {rule.methods}" for rule in app.url_map.iter_rules()]
    })

    return app

if __name__ == "__main__":
    # Use development config with SQLite for local testing
    import os
    os.environ['FLASK_ENV'] = 'development'
    os.environ['DATABASE_URL'] = 'sqlite:///test_supplyline.db'

    app = create_app('development')
    app.run(host="0.0.0.0", port=5000, debug=True)