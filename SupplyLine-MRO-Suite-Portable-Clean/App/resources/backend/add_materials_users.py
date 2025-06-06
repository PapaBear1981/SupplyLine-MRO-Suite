from models import db, User
from flask import Flask
import os

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

def add_materials_users():
    with app.app_context():
        # Create funny test users in the Materials department
        materials_users = [
            {
                'name': 'Stocky McStockface',
                'employee_number': 'MAT001',
                'department': 'Materials',
                'password': 'password123',
                'is_admin': False
            },
            {
                'name': 'Inventory Master',
                'employee_number': 'MAT002',
                'department': 'Materials',
                'password': 'password123',
                'is_admin': False
            },
            {
                'name': 'Shelf Stacker',
                'employee_number': 'MAT003',
                'department': 'Materials',
                'password': 'password123',
                'is_admin': False
            }
        ]
        
        # Add users to database
        for user_data in materials_users:
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
        print("Materials users added successfully!")

if __name__ == "__main__":
    add_materials_users()
    print("\nLogin credentials for all Materials users:")
    print("Employee Number: MAT001-MAT003")
    print("Password: password123")
