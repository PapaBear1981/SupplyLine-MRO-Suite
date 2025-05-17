from flask import Flask, session
from routes import register_routes
from config import Config
from flask_session import Session
from flask_cors import CORS
import os
import sys

def create_app():
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

    register_routes(app)

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