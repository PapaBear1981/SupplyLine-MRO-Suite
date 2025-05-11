from models import db, User, Tool, Checkout, AuditLog
from flask import Flask
import os
import sqlite3

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

with app.app_context():
    # Backup existing data
    users = User.query.all()
    tools = Tool.query.all()
    checkouts = Checkout.query.all()
    audit_logs = AuditLog.query.all()
    
    print(f"Backing up {len(users)} users, {len(tools)} tools, {len(checkouts)} checkouts, {len(audit_logs)} audit logs")
    
    # Store user data
    user_data = []
    for user in users:
        user_data.append({
            'name': user.name,
            'employee_number': user.employee_number,
            'department': user.department,
            'password_hash': user.password_hash,
            'is_admin': user.is_admin,
            'created_at': user.created_at
        })
    
    # Store tool data
    tool_data = []
    for tool in tools:
        tool_data.append({
            'tool_number': tool.tool_number,
            'serial_number': tool.serial_number,
            'description': tool.description,
            'condition': tool.condition,
            'location': tool.location,
            'created_at': tool.created_at
        })
    
    # Store checkout data
    checkout_data = []
    for checkout in checkouts:
        checkout_data.append({
            'tool_id': checkout.tool_id,
            'user_id': checkout.user_id,
            'checkout_date': checkout.checkout_date,
            'return_date': checkout.return_date,
            'expected_return_date': checkout.expected_return_date
        })
    
    # Store audit log data
    audit_log_data = []
    for log in audit_logs:
        audit_log_data.append({
            'action_type': log.action_type,
            'action_details': log.action_details,
            'timestamp': log.timestamp
        })
    
    # Drop and recreate all tables
    print("Dropping and recreating all tables...")
    db.drop_all()
    db.create_all()
    
    # Restore user data
    print("Restoring user data...")
    for user_info in user_data:
        user = User(**user_info)
        db.session.add(user)
    db.session.commit()
    
    # Restore tool data with category
    print("Restoring tool data with category...")
    for tool_info in tool_data:
        # Add category field
        tool_info['category'] = 'General'  # Default category
        tool = Tool(**tool_info)
        db.session.add(tool)
    db.session.commit()
    
    # Restore checkout data
    print("Restoring checkout data...")
    for checkout_info in checkout_data:
        checkout = Checkout(**checkout_info)
        db.session.add(checkout)
    db.session.commit()
    
    # Restore audit log data
    print("Restoring audit log data...")
    for log_info in audit_log_data:
        log = AuditLog(**log_info)
        db.session.add(log)
    db.session.commit()
    
    print("Database recreation completed successfully!")
