import os

from socketio_config import socketio

from app import create_app


app = create_app()

if __name__ == "__main__":
    # Get debug mode from environment variable, default to False for security
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")

    # Only print routes in debug mode
    if debug_mode:
        print("\n=== Registered Routes ===")
        for rule in app.url_map.iter_rules():
            print(f"{rule} - {rule.methods}")
        print("========================\n")

    # Bind to 127.0.0.1 by default for security, allow override via environment
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", 5000))

    # Use socketio.run() instead of app.run() for WebSocket support
    # allow_unsafe_werkzeug=True is needed for production deployment
    socketio.run(app, host=host, port=port, debug=debug_mode, allow_unsafe_werkzeug=True)
