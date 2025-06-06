from models import db, User
from flask import Flask
import os

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

with app.app_context():
    # Get admin user
    admin = User.query.filter_by(employee_number='ADMIN001').first()

    if not admin:
        print("Admin user not found!")
    else:
        print(f"Found admin user: {admin.name} ({admin.employee_number})")

        # Validate admin setup security
        from utils.admin_init import validate_admin_setup
        is_secure, issues = validate_admin_setup()

        print(f"Admin setup security status: {'SECURE' if is_secure else 'INSECURE'}")

        if issues:
            print("Security issues found:")
            for issue in issues:
                print(f"  - {issue}")

        if not is_secure:
            print("\nWARNING: Admin setup has security vulnerabilities!")
            print("Consider running secure admin reset or setting INITIAL_ADMIN_PASSWORD environment variable.")
        else:
            print("Admin setup appears secure.")
