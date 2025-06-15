from backend.models import db, User
from flask import Flask
import os

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

with app.app_context():
    # Check if database exists
    users = User.query.all()
    
    if not users:
        print("No users found in the database!")
    else:
        print(f"Found {len(users)} users in the database:")
        for user in users:
            print(f"ID: {user.id}, Name: {user.name}, Employee Number: {user.employee_number}, Department: {user.department}, Admin: {user.is_admin}")
