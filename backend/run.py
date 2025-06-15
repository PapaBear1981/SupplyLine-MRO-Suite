from backend.app import create_app

app = create_app()

def print_routes():
    """Print all registered routes for debugging"""
    print("\n=== Registered Routes ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule} - {rule.methods}")
    print("========================\n")

if __name__ == "__main__":
    import os

    # Print routes immediately
    with app.app_context():
        print_routes()

    # Use PORT environment variable for Cloud Run compatibility
    port = int(os.environ.get("PORT", 5000))
    # Only enable debug mode in development
    debug = os.environ.get("FLASK_ENV") == "development"

    app.run(host="0.0.0.0", port=port, debug=debug)
