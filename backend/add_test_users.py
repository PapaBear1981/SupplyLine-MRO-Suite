from backend.models import db, User
from flask import Flask
import os

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

def add_test_users():
    with app.app_context():
        # Create funny test users in the Maintenance department
        test_users = [
            {
                'name': 'Rusty Nailbender',
                'employee_number': 'MAINT001',
                'department': 'Maintenance',
                'password': 'password123',
                'is_admin': False
            },
            {
                'name': 'Sparky McShockface',
                'employee_number': 'MAINT002',
                'department': 'Maintenance',
                'password': 'password123',
                'is_admin': False
            },
            {
                'name': 'Wrench Thrower',
                'employee_number': 'MAINT003',
                'department': 'Maintenance',
                'password': 'password123',
                'is_admin': False
            },
            {
                'name': 'Leaky Pipes',
                'employee_number': 'MAINT004',
                'department': 'Maintenance',
                'password': 'password123',
                'is_admin': False
            },
            {
                'name': 'Dusty Sawdust',
                'employee_number': 'MAINT005',
                'department': 'Maintenance',
                'password': 'password123',
                'is_admin': False
            }
        ]
        
        # Add users to database
        for user_data in test_users:
            # Check if user already exists
            existing_user = User.query.filter_by(employee_number=user_data['employee_number']).first()
            if existing_user:
                print(f"User {user_data['name']} already exists, skipping...")
                continue
                
            # Create new user
            user = User(
                name=user_data['name'],
                employee_number=user_data['employee_number'],
                department=user_data['department'],
                is_admin=user_data['is_admin']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            print(f"Added user: {user_data['name']} ({user_data['employee_number']})")
        
        db.session.commit()
        print("Test users added successfully!")

if __name__ == "__main__":
    add_test_users()
    print("\nLogin credentials for all test users:")
    print("Employee Number: MAINT001-MAINT005")
    print("Password: password123")
