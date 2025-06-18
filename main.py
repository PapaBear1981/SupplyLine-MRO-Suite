import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app import create_app

# Create the Flask application instance for Gunicorn
app = create_app()

if __name__ == "__main__":
    # Use PORT environment variable for Cloud Run compatibility
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
