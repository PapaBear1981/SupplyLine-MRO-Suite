from flask import Flask, session, request, Response
from routes import register_routes
from config import Config
from flask_session import Session
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from rate_limiter import init_limiter
import os
import sys
import logging

def create_app(config_class=Config):
    # serve frontend static files from backend/static
    app = Flask(
        __name__,
        instance_relative_config=False,
        static_folder='static',
        static_url_path=''
    )
    app.config.from_object(config_class)

    # Configure logging
    if app.config.get('FLASK_ENV') == 'production':
        # In production, log to file
        logging.basicConfig(
            filename='app.log',
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # In development, log to console
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    # Initialize CSRF protection
    csrf = CSRFProtect(app)

    # Initialize rate limiter
    init_limiter(app)

    # Initialize CORS with settings from config
    CORS(app,
         resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}},
         supports_credentials=app.config['CORS_SUPPORTS_CREDENTIALS'])

    # Initialize Flask-Session
    Session(app)

    # Add security headers to all responses
    @app.after_request
    def add_security_headers(response):
        # Add security headers from config
        for header, value in app.config.get('SECURITY_HEADERS', {}).items():
            if value is not None:
                response.headers[header] = value

        # Add Content-Security-Policy header
        csp_config = app.config.get('CONTENT_SECURITY_POLICY', {})
        if csp_config:
            csp_value = '; '.join([f"{key} {value}" for key, value in csp_config.items()])
            response.headers['Content-Security-Policy'] = csp_value

        return response

    # Log all requests in production for security auditing
    @app.before_request
    def log_request_info():
        if app.config.get('FLASK_ENV') == 'production':
            app.logger.info(f'Request: {request.method} {request.path} from {request.remote_addr}')

    # Handle CSRF errors gracefully
    @csrf.error_handler
    def handle_csrf_error(reason):
        return Response(
            '{"error": "CSRF validation failed. Please refresh the page and try again."}',
            status=400,
            mimetype='application/json'
        )

    # Run database migrations
    try:
        # Import and run the reorder fields migration
        from migrate_reorder_fields import migrate_database
        print("Running chemical reorder fields migration...")
        migrate_database()
    except Exception as e:
        print(f"Error running chemical reorder fields migration: {str(e)}")

    try:
        # Import and run the tool calibration migration
        from migrate_tool_calibration import migrate_database as migrate_tool_calibration
        print("Running tool calibration migration...")
        migrate_tool_calibration()
    except Exception as e:
        print(f"Error running tool calibration migration: {str(e)}")

    try:
        # Import and run the registration IP address migration
        from migrate_registration_ip import migrate_database as migrate_registration_ip
        print("Running registration IP address migration...")
        migrate_registration_ip()
    except Exception as e:
        print(f"Error running registration IP address migration: {str(e)}")

    register_routes(app)

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    # Only print routes in development mode
    if not app.config.get('FLASK_ENV') == 'production':
        print("\n=== Registered Routes ===")
        for rule in app.url_map.iter_rules():
            print(f"{rule} - {rule.methods}")
        print("========================\n")

    return app

if __name__ == "__main__":
    app = create_app()
    # Only enable debug mode in development
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)