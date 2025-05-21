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
        static_url_path=''
    )
    app.config.from_object(Config)

    # Initialize CORS with settings from config
    CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"], "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}}, supports_credentials=True)

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

    # Register main routes
    register_routes(app)

    # Direct time endpoints
    @app.route('/api/time')
    def time_endpoint():
        try:
            from time_utils import get_utc_timestamp, get_local_timestamp, format_datetime
            return jsonify({
                'status': 'ok',
                'utc_time': format_datetime(get_utc_timestamp()),
                'local_time': format_datetime(get_local_timestamp()),
                'timezone': str(time.tzname),
                'using_time_utils': True
            })
        except ImportError:
            return jsonify({
                'status': 'ok',
                'utc_time': datetime.datetime.now().isoformat(),
                'local_time': datetime.datetime.now().isoformat(),
                'timezone': str(time.tzname),
                'using_time_utils': False
            })

    @app.route('/api/time-test')
    def time_test():
        return jsonify({
            'status': 'ok',
            'utc_time': datetime.datetime.now().isoformat(),
            'local_time': datetime.datetime.now().isoformat(),
            'timezone': str(time.tzname),
            'message': 'This is a test endpoint for time functionality'
        })

    # Try to register time API blueprint (but we have direct endpoints as backup)
    try:
        from time_api import time_api
        app.register_blueprint(time_api)
        print("Registered time_api blueprint")
    except ImportError as e:
        print(f"Error importing time_api blueprint: {str(e)}")

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