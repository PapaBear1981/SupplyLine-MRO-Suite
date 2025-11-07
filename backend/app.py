import atexit
import datetime
import logging.config
import os
import time

from flask import Flask

# from flask_session import Session  # Disabled due to Flask 3.x compatibility issues - using JWT instead
from flask_cors import CORS

from config import Config
from models import db
from routes import register_routes
from socketio_config import init_socketio
from utils.logging_utils import setup_request_logging
from utils.resource_monitor import init_resource_monitoring
from utils.scheduled_backup import init_scheduled_backup, shutdown_scheduled_backup
from utils.scheduled_maintenance import init_scheduled_maintenance, shutdown_scheduled_maintenance


def create_app():
    # Set the system timezone to UTC
    os.environ["TZ"] = "UTC"
    try:
        time.tzset()
        print("System timezone set to UTC")  # Keep this as print since logging not yet configured
    except AttributeError:
        # Windows doesn't have time.tzset()
        print("Running on Windows, cannot set system timezone. Ensure system time is correct.")

    # serve frontend static files from backend/static
    app = Flask(
        __name__,
        instance_relative_config=False,
        static_folder="static",
        static_url_path="/static"
    )
    app.config.from_object(Config)

    # File upload safeguards
    app.config.setdefault("MAX_AVATAR_FILE_SIZE", 5 * 1024 * 1024)  # 5MB
    app.config.setdefault("MAX_BULK_IMPORT_FILE_SIZE", 5 * 1024 * 1024)
    app.config.setdefault("MAX_CALIBRATION_CERTIFICATE_FILE_SIZE", 5 * 1024 * 1024)
    app.config.setdefault(
        "CALIBRATION_CERTIFICATE_FOLDER",
        os.path.join(app.instance_path, "calibration_certificates")
    )
    os.makedirs(app.config["CALIBRATION_CERTIFICATE_FOLDER"], exist_ok=True)

    # Ensure session storage is configured with a supported backend
    session_type = app.config.get("SESSION_TYPE")
    if not session_type or session_type.lower() == "null":
        app.config["SESSION_TYPE"] = "filesystem"

    if app.config["SESSION_TYPE"] == "filesystem":
        session_dir = app.config.get("SESSION_FILE_DIR") or os.path.join(app.instance_path, "flask_session")
        os.makedirs(session_dir, exist_ok=True)
        app.config["SESSION_FILE_DIR"] = session_dir

    # Allow runtime overrides of the database URL (useful for tests)
    runtime_db_url = os.environ.get("DATABASE_URL")
    if runtime_db_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = runtime_db_url

    # Normalize engine options when using SQLite (particularly in tests)
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri.startswith("sqlite"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "echo": False,
            "pool_pre_ping": True,
            "connect_args": {"check_same_thread": False},
        }

    # Determine if we're running in a testing environment
    is_testing_env = bool(
        app.config.get("TESTING")
        or os.environ.get("FLASK_ENV") == "testing"
        or os.environ.get("PYTEST_CURRENT_TEST")
    )
    if is_testing_env:
        app.config["TESTING"] = True

    # Validate security configuration (deferred to allow test fixtures to set values)
    Config.validate_security_config(app.config)

    # Configure structured logging
    if hasattr(Config, "LOGGING_CONFIG"):
        try:
            logging.config.dictConfig(Config.LOGGING_CONFIG)
            logging.getLogger(__name__).info("Structured logging configured successfully")
        except Exception as e:
            logging.getLogger(__name__).warning("Error configuring logging: %s", e)
            # Fall back to basic logging
            logging.basicConfig(level=logging.INFO)

    # Initialize CORS with settings from config
    allowed_origins = app.config.get("CORS_ORIGINS", ["http://localhost:5173"])
    allow_headers = app.config.get("CORS_ALLOW_HEADERS", [
        "Content-Type",
        "Authorization",
        "X-CSRF-Token",
    ])
    supports_credentials = app.config.get("CORS_SUPPORTS_CREDENTIALS", False)
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": allowed_origins,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": allow_headers,
                "supports_credentials": supports_credentials,
            },
            r"/tool-view/*": {
                "origins": allowed_origins,
                "methods": ["GET", "OPTIONS"],
                "allow_headers": allow_headers,
                "supports_credentials": supports_credentials,
            },
            r"/chemical-view/*": {
                "origins": allowed_origins,
                "methods": ["GET", "OPTIONS"],
                "allow_headers": allow_headers,
                "supports_credentials": supports_credentials,
            }
        },
    )

    # Ensure session storage is configured (default to secure filesystem storage)
    session_type = app.config.get("SESSION_TYPE")
    if not session_type or str(session_type).lower() in {"none", "null", ""}:
        app.config["SESSION_TYPE"] = "filesystem"

    # Initialize Flask-Session - DISABLED due to Flask 3.x compatibility issues
    # The application uses JWT authentication, so Flask-Session is not needed
    # Session(app)

    # Initialize session cleanup - DISABLED since Flask-Session is disabled
    # init_session_cleanup(app)

    # Initialize resource monitoring
    init_resource_monitoring(app)

    # Setup request logging middleware
    setup_request_logging(app)

    # Initialize database with app
    db.init_app(app)

    # Initialize SocketIO for real-time messaging
    init_socketio(app)

    # Register WebSocket event handlers
    from socketio_events import register_socketio_events
    register_socketio_events(app)

    # Get logger after logging is configured
    logger = logging.getLogger(__name__)

    # Load persisted security settings (e.g., inactivity timeout)
    try:
        from utils.system_settings import load_security_settings

        timeout_minutes = load_security_settings(app)
        logger.info(
            "Loaded security settings",
            extra={"session_timeout_minutes": timeout_minutes},
        )
    except Exception as exc:
        logger.error(
            "Failed to load security settings",
            exc_info=True,
            extra={"error_message": str(exc)},
        )

    # Log current time information for debugging
    logger.info("Application starting", extra={
        "utc_time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "local_time": datetime.datetime.now().isoformat()
    })

    # Database migrations have been applied and are managed through the migrations/ directory
    # No inline migrations needed at startup

    # Setup global error handlers
    from utils.error_handler import setup_global_error_handlers
    setup_global_error_handlers(app)

    # Create database tables (after all setup is complete)
    if not is_testing_env:
        try:
            logger.info("Creating database tables...")
            with app.app_context():
                db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error("Error creating database tables", exc_info=True, extra={
                "error_message": str(e)
            })
            raise
    else:
        logger.info("Skipping automatic database table creation in testing mode")

    # Create admin user if it doesn't exist (after tables are created)
    if not is_testing_env:
        try:
            from utils.admin_init import create_secure_admin
            logger.info("Checking/creating admin user...")
            with app.app_context():
                success, message, password = create_secure_admin()
                if success:
                    logger.warning("SECURITY NOTICE: Admin user created successfully")
                    if password:
                        logger.warning("INITIAL ADMIN PASSWORD GENERATED - copy from env-var not from logs")
                else:
                    logger.error(f"Failed to create admin user: {message}")
        except Exception as e:
            logger.error("Error during admin user creation", exc_info=True, extra={
                "error_message": str(e)
            })

    # Register main routes
    register_routes(app)

    # Add security headers middleware
    @app.after_request
    def add_security_headers(response):
        security_headers = app.config.get("SECURITY_HEADERS", {})
        for header, value in security_headers.items():
            response.headers[header] = value
        return response

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    # Log all registered routes for debugging
    logger.info("Application routes registered", extra={
        "route_count": len(list(app.url_map.iter_rules())),
        "routes": [f"{rule} - {rule.methods}" for rule in app.url_map.iter_rules()]
    })

    # Initialize scheduled backup service
    if not is_testing_env:
        try:
            logger.info("Initializing scheduled backup service...")
            init_scheduled_backup(app)

            # Register cleanup on shutdown
            atexit.register(shutdown_scheduled_backup)

            logger.info("Scheduled backup service initialized")
        except Exception as e:
            logger.error("Error initializing scheduled backup service", exc_info=True, extra={
                "error_message": str(e)
            })

    # Initialize scheduled maintenance service
    if not is_testing_env:
        try:
            logger.info("Initializing scheduled maintenance service...")
            init_scheduled_maintenance(app)

            # Register cleanup on shutdown
            atexit.register(shutdown_scheduled_maintenance)

            logger.info("Scheduled maintenance service initialized")
        except Exception as e:
            logger.error("Error initializing scheduled maintenance service", exc_info=True, extra={
                "error_message": str(e)
            })

    return app

if __name__ == "__main__":
    app = create_app()

    # Determine host and debug settings based on environment variables (Bandit B104, B201 mitigation)
    # Default to secure settings (127.0.0.1, debug=False) unless FLASK_ENV is 'development'
    is_development = os.environ.get("FLASK_ENV") == "development"

    # B104: Restrict host binding unless explicitly set or in development
    # nosec B104: Binding to 0.0.0.0 is intentional in development/Docker environments
    # In production, this should be overridden via FLASK_RUN_HOST environment variable
    host = os.environ.get("FLASK_RUN_HOST", "0.0.0.0" if is_development else "127.0.0.1")  # nosec B104
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    # B201: Disable debug unless explicitly set or in development
    debug = os.environ.get("FLASK_DEBUG", "True" if is_development else "False").lower() in ("true", "1", "yes")

    app.run(host=host, port=port, debug=debug)
