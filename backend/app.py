from flask import Flask, session
from routes import register_routes
from config import Config
from flask_session import Session
from flask_cors import CORS

def create_app():
    # serve frontend static files from backend/static
    app = Flask(
        __name__,
        instance_relative_config=False,
        static_folder='static',
        static_url_path=''
    )
    app.config.from_object(Config)

    # Initialize CORS with more permissive settings for development
    CORS(app,
         supports_credentials=True,
         origins=["http://localhost:5173", "http://127.0.0.1:5173"],
         allow_headers=["Content-Type", "Authorization"],
         expose_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Initialize Flask-Session
    Session(app)

    register_routes(app)

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)