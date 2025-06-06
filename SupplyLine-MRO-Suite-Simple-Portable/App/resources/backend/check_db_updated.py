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
    
    # Check if tools have category
    if tools:
        for tool in tools[:3]:  # Just check first 3 tools
            try:
                print(f"Tool {tool.id}: Tool Number = {tool.tool_number}, Category = {tool.category}")
            except AttributeError:
                print(f"Tool {tool.id}: Tool Number = {tool.tool_number}, Category attribute is missing")
                
    # Check if the expected_return_date column exists in checkouts
    if checkouts:
        for checkout in checkouts[:3]:  # Just check first 3 checkouts
            try:
                print(f"Checkout {checkout.id}: Expected Return Date = {checkout.expected_return_date}")
            except AttributeError:
                print(f"Checkout {checkout.id}: Expected Return Date attribute is missing")
