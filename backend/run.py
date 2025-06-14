from app import create_app

app = create_app()

def print_routes():
    """Print all registered routes for debugging"""
    print("\n=== Registered Routes ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule} - {rule.methods}")
    print("========================\n")

if __name__ == "__main__":
    # Print routes immediately
    with app.app_context():
        print_routes()
    app.run(host="0.0.0.0", port=5000, debug=True)
