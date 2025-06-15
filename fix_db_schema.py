from backend.models import db, Tool, User, Checkout, AuditLog
from flask import Flask
import os
import sqlite3

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'tools.db')
db_path = os.path.abspath(db_path)
print(f"Using database at: {db_path}")

# Connect to the database directly with sqlite3
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if the category column already exists
cursor.execute("PRAGMA table_info(tools)")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]

if 'category' not in column_names:
    # Add the category column to the tools table
    cursor.execute("ALTER TABLE tools ADD COLUMN category TEXT DEFAULT 'General'")
    print("Added 'category' column to tools table")
    conn.commit()
else:
    print("'category' column already exists in tools table")

# Close the sqlite connection
conn.close()

# Now restart the Flask app to pick up the schema changes
with app.app_context():
    # Check if the changes were applied
    tools = Tool.query.all()
    if tools:
        for tool in tools[:3]:  # Just check first 3 tools
            try:
                print(f"Tool {tool.id}: Tool Number = {tool.tool_number}, Category = {tool.category}")
            except AttributeError:
                print(f"Tool {tool.id}: Tool Number = {tool.tool_number}, Category attribute is missing")
    
    # Update all tools to have a category if they don't already
    print("Updating all tools to have a category...")
    for tool in tools:
        if not tool.category:
            tool.category = 'General'
    db.session.commit()
    
    print("Database schema update completed successfully!")
