from models import db, Tool
from flask import Flask
import os

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

with app.app_context():
    # Check if tools exist
    tools = Tool.query.all()
    
    if not tools:
        print("No tools found in the database!")
    else:
        print(f"Found {len(tools)} tools in the database:")
        for tool in tools:
            print(f"ID: {tool.id}, Tool Number: {tool.tool_number}, Serial Number: {tool.serial_number}, Description: {tool.description}, Category: {tool.category}")
