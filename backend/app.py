from flask import Flask, session, jsonify
from routes import register_routes
from config import Config
from flask_session import Session
from flask_cors import CORS
import os
import sys
import time
import datetime

def create_app():
    # Set the system timezone to UTC
    os.environ['TZ'] = 'UTC'
    try:
        time.tzset()
        print("System timezone set to UTC")
    except AttributeError:
        # Windows doesn't have time.tzset()
        print("Running on Windows, cannot set system timezone. Ensure system time is correct.")

    # serve frontend static files from backend/static
    app = Flask(
        __name__,
        instance_relative_config=False,
        static_folder='static',
        static_url_path='/static'
    )
    app.config.from_object(Config)

    # Initialize CORS with settings from config
    allowed_origins = app.config.get('CORS_ORIGINS', ['http://localhost:5173'])
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-CSRF-Token"],
            "supports_credentials": True
        }
    })

    # Initialize Flask-Session
    Session(app)

    # Log current time information for debugging
    print(f"Current UTC time: {datetime.datetime.now(datetime.timezone.utc)}")
    print(f"Current local time: {datetime.datetime.now()}")

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
        # Import and run the performance indexes migration
        from migrate_performance_indexes import migrate_database as migrate_performance_indexes
        print("Running performance indexes migration...")
        migrate_performance_indexes()
    except Exception as e:
        print(f"Error running performance indexes migration: {str(e)}")

    # Setup global error handlers
    from utils.error_handler import setup_global_error_handlers
    setup_global_error_handlers(app)

    # Register main routes
    register_routes(app)

    # Add security headers middleware
    @app.after_request
    def add_security_headers(response):
        security_headers = app.config.get('SECURITY_HEADERS', {})
        for header, value in security_headers.items():
            response.headers[header] = value
        return response

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    # Print all registered routes for debugging
    print("\n=== Registered Routes ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule} - {rule.methods}")
    print("========================\n")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)