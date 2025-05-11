import os
import sqlite3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create a minimal Flask app
app = Flask(__name__)

# Define the database path
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'tools.db'))
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define a simple model
class Test(db.Model):
    __tablename__ = 'test'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

# Create the test table
with app.app_context():
    db.create_all()
    print("Database tables created")

    # Try to insert a test record
    test = Test(name='Test Record')
    db.session.add(test)
    db.session.commit()
    print("Test record inserted")

    # Query the test record
    test_record = Test.query.first()
    print(f"Test record: {test_record.name}")

print("Test completed successfully")
