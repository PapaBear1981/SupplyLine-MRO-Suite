from app import create_app

app = create_app()

if __name__ == "__main__":
    # Print all registered routes for debugging
    print("\n=== Registered Routes ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule} - {rule.methods}")
    print("========================\n")

    app.run(host="0.0.0.0", port=5000, debug=True)
