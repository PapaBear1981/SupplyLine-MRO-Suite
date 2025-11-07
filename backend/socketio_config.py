"""
WebSocket configuration and initialization for real-time messaging.
"""
from flask_socketio import SocketIO


# Initialize SocketIO with async mode for production
# cors_allowed_origins will be set dynamically from app config
socketio = SocketIO(
    cors_allowed_origins="*",  # Will be restricted in production via app config
    async_mode="threading",  # Use threading for compatibility with gunicorn
    logger=True,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25
)


def init_socketio(app):
    """
    Initialize SocketIO with the Flask app and configure CORS.

    Args:
        app: Flask application instance
    """
    # Get allowed origins from config
    allowed_origins = app.config.get("CORS_ORIGINS", ["http://localhost:5173"])

    # Update SocketIO configuration
    socketio.init_app(
        app,
        cors_allowed_origins=allowed_origins,
        async_mode="threading",
        logger=app.config.get("DEBUG", False),
        engineio_logger=False,
        ping_timeout=60,
        ping_interval=25,
        manage_session=False  # We use JWT authentication instead
    )

    app.logger.info(
        "SocketIO initialized",
        extra={"allowed_origins": allowed_origins, "async_mode": "threading"}
    )

    return socketio
