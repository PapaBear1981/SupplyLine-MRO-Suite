from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == "__main__":
    import os
    # Use PORT environment variable for Cloud Run compatibility
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
