from models import db, Tool, User, Checkout, AuditLog
from flask import Flask
import os

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

with app.app_context():
    # Check database tables
    users = User.query.all()
    tools = Tool.query.all()
    checkouts = Checkout.query.all()
    audit_logs = AuditLog.query.all()

    print(f"Users: {len(users)}")
    print(f"Tools: {len(tools)}")
    print(f"Checkouts: {len(checkouts)}")
    print(f"Audit Logs: {len(audit_logs)}")

    # Show tool details
    print("\nTool Details:")
    if tools:
        for tool in tools[:5]:  # Show first 5 tools
            print(f"Tool ID: {tool.id}, Number: {tool.tool_number}, Serial: {tool.serial_number}, Description: {tool.description}")

            # Check if tool is currently checked out
            active_checkout = Checkout.query.filter_by(tool_id=tool.id, return_date=None).first()
            status = 'checked_out' if active_checkout else 'available'
            print(f"  Status: {status}")

    # Show active checkouts
    print("\nActive Checkouts:")
    active_checkouts = Checkout.query.filter(Checkout.return_date.is_(None)).all()
    if active_checkouts:
        for checkout in active_checkouts:
            tool = Tool.query.get(checkout.tool_id)
            user = User.query.get(checkout.user_id)
            print(f"Checkout ID: {checkout.id}, Tool: {tool.tool_number} (ID: {tool.id}), User: {user.name} (ID: {user.id})")
            print(f"  Checkout Date: {checkout.checkout_date}, Expected Return: {checkout.expected_return_date}")
    else:
        print("  No active checkouts found.")
