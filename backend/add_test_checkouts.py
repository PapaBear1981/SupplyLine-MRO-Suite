from backend.models import db, Tool, User, Checkout
from flask import Flask
from datetime import datetime, timedelta
import os
import random

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

def add_test_checkouts():
    with app.app_context():
        # Get all tools
        tools = Tool.query.all()
        
        # Get maintenance users
        maintenance_users = User.query.filter_by(department='Maintenance').all()
        
        if not tools:
            print("No tools found in the database!")
            return
            
        if not maintenance_users:
            print("No maintenance users found in the database!")
            return
            
        # Create some active checkouts
        active_checkouts = []
        
        # Assign tool 3 to Rusty
        rusty = User.query.filter_by(employee_number='MAINT001').first()
        if rusty and len(tools) >= 3:
            checkout = Checkout(
                tool_id=tools[2].id,  # Tool 3
                user_id=rusty.id,
                checkout_date=datetime.now() - timedelta(days=1),
                expected_return_date=datetime.now() + timedelta(days=6)
            )
            active_checkouts.append(checkout)
            print(f"Created active checkout: {tools[2].tool_number} to {rusty.name}")
            
        # Assign tool 4 to Sparky
        sparky = User.query.filter_by(employee_number='MAINT002').first()
        if sparky and len(tools) >= 4:
            checkout = Checkout(
                tool_id=tools[3].id,  # Tool 4
                user_id=sparky.id,
                checkout_date=datetime.now() - timedelta(days=3),
                expected_return_date=datetime.now() + timedelta(days=4)
            )
            active_checkouts.append(checkout)
            print(f"Created active checkout: {tools[3].tool_number} to {sparky.name}")
            
        # Create some past checkouts (returned)
        past_checkouts = []
        
        # Past checkout for Wrench Thrower
        wrench = User.query.filter_by(employee_number='MAINT003').first()
        if wrench and len(tools) >= 5:
            checkout = Checkout(
                tool_id=tools[4].id,  # Tool 5
                user_id=wrench.id,
                checkout_date=datetime.now() - timedelta(days=10),
                return_date=datetime.now() - timedelta(days=5),
                expected_return_date=datetime.now() - timedelta(days=3)
            )
            past_checkouts.append(checkout)
            print(f"Created past checkout: {tools[4].tool_number} to {wrench.name}")
            
        # Past checkout for Leaky Pipes
        leaky = User.query.filter_by(employee_number='MAINT004').first()
        if leaky and len(tools) >= 2:
            checkout = Checkout(
                tool_id=tools[1].id,  # Tool 2
                user_id=leaky.id,
                checkout_date=datetime.now() - timedelta(days=15),
                return_date=datetime.now() - timedelta(days=12),
                expected_return_date=datetime.now() - timedelta(days=8)
            )
            past_checkouts.append(checkout)
            print(f"Created past checkout: {tools[1].tool_number} to {leaky.name}")
            
        # Add all checkouts to the database
        db.session.add_all(active_checkouts + past_checkouts)
        db.session.commit()
        
        print(f"Added {len(active_checkouts)} active checkouts and {len(past_checkouts)} past checkouts")

if __name__ == "__main__":
    add_test_checkouts()
