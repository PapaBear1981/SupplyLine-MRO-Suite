from models import db, Tool, User, Checkout
from flask import Flask
from datetime import datetime, timedelta
import os

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

def seed_database():
    with app.app_context():
        # Clear existing data
        Checkout.query.delete()
        Tool.query.delete()

        # Keep users intact to preserve login credentials

        # Create sample tools
        tools = [
            Tool(
                tool_number='T001',
                serial_number='SN12345',
                description='Power Drill - 18V',
                condition='Good',
                location='Main Warehouse'
            ),
            Tool(
                tool_number='T002',
                serial_number='SN67890',
                description='Circular Saw - 7 1/4"',
                condition='Excellent',
                location='Tool Room A'
            ),
            Tool(
                tool_number='T003',
                serial_number='SN11223',
                description='Hammer - 16oz',
                condition='Fair',
                location='Tool Room B'
            ),
            Tool(
                tool_number='T004',
                serial_number='SN44556',
                description='Impact Driver - 20V',
                condition='Good',
                location='Main Warehouse'
            ),
            Tool(
                tool_number='T005',
                serial_number='SN77889',
                description='Tape Measure - 25ft',
                condition='Excellent',
                location='Tool Room A'
            )
        ]

        db.session.add_all(tools)
        db.session.commit()

        print(f"Added {len(tools)} tools to the database")

        # Get admin user for checkouts
        admin = User.query.filter_by(employee_number='ADMIN001').first()

        if admin:
            # Create some checkouts
            # Active checkout
            checkout1 = Checkout(
                tool_id=tools[0].id,
                user_id=admin.id,
                checkout_date=datetime.utcnow() - timedelta(days=2),
                expected_return_date=datetime.utcnow() + timedelta(days=5)
            )

            # Returned checkout
            checkout2 = Checkout(
                tool_id=tools[1].id,
                user_id=admin.id,
                checkout_date=datetime.utcnow() - timedelta(days=5),
                return_date=datetime.utcnow() - timedelta(days=3),
                expected_return_date=datetime.utcnow() - timedelta(days=1)
            )

            db.session.add_all([checkout1, checkout2])
            db.session.commit()

            print(f"Added 2 checkouts for admin user")
        else:
            print("Admin user not found. No checkouts created.")

if __name__ == "__main__":
    seed_database()
    print("Database seeded successfully!")
