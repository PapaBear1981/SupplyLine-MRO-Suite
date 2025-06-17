from models import db, User
from flask import Flask
import os

# Create a minimal Flask app
app = Flask(__name__)

# Use the same database path as the main application
db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'tools.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'development-key'

print(f"Using database: {db_path}")

# Initialize the database
db.init_app(app)

with app.app_context():
    # Create tables if they don't exist
    db.create_all()

    # Get admin user
    admin = User.query.filter_by(employee_number='ADMIN001').first()

    if not admin:
        print("Admin user not found! Creating new admin user...")

        # Create admin user
        admin = User(
            name='System Administrator',
            employee_number='ADMIN001',
            department='IT',
            is_admin=True,
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

        print("✓ Admin user created with password 'admin123'")
    else:
        print(f"Found admin user: {admin.name} ({admin.employee_number})")

        # Reset password to admin123
        admin.set_password('admin123')
        db.session.commit()

        print("Admin password reset to 'admin123'")

    # Verify the password works
    if admin.check_password('admin123'):
        print("✓ Password verification successful")
    else:
        print("✗ Password verification failed")
