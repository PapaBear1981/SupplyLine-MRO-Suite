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
            print(f"Tool {tool.id}: Category = {tool.category}")
