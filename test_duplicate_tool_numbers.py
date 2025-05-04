from flask import Flask
from models import db, Tool
import os
import sys

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'database', 'tools.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

def test_duplicate_tool_numbers():
    """Test creating tools with the same tool number but different serial numbers"""
    with app.app_context():
        # Create test tools with the same tool number but different serial numbers
        tool_number = "HT001"  # Heat gun tool number
        
        # Create first heat gun
        tool1 = Tool(
            tool_number=tool_number,
            serial_number="001",
            description="Heat Gun - Unit 1",
            condition="Good",
            location="Storage A"
        )
        db.session.add(tool1)
        db.session.commit()
        print(f"Created first heat gun: {tool1.tool_number} with serial {tool1.serial_number}")
        
        # Create second heat gun
        tool2 = Tool(
            tool_number=tool_number,
            serial_number="002",
            description="Heat Gun - Unit 2",
            condition="Good",
            location="Storage B"
        )
        db.session.add(tool2)
        db.session.commit()
        print(f"Created second heat gun: {tool2.tool_number} with serial {tool2.serial_number}")
        
        # Create third heat gun
        tool3 = Tool(
            tool_number=tool_number,
            serial_number="003",
            description="Heat Gun - Unit 3",
            condition="New",
            location="Storage C"
        )
        db.session.add(tool3)
        db.session.commit()
        print(f"Created third heat gun: {tool3.tool_number} with serial {tool3.serial_number}")
        
        # Verify we can retrieve all three tools
        heat_guns = Tool.query.filter_by(tool_number=tool_number).all()
        print(f"Found {len(heat_guns)} heat guns with tool number {tool_number}:")
        for gun in heat_guns:
            print(f"  ID: {gun.id}, Tool Number: {gun.tool_number}, Serial: {gun.serial_number}, Description: {gun.description}")
        
        # Try to create a tool with duplicate tool number AND serial number (should fail in the API)
        try:
            duplicate_tool = Tool(
                tool_number=tool_number,
                serial_number="001",  # Same as tool1
                description="Duplicate Heat Gun",
                condition="Fair",
                location="Storage D"
            )
            db.session.add(duplicate_tool)
            db.session.commit()
            print("WARNING: Created duplicate tool with same tool number AND serial number!")
        except Exception as e:
            print(f"Expected error when creating duplicate tool: {str(e)}")
            db.session.rollback()
        
        # Clean up test data
        if input("Do you want to remove the test tools? (y/n): ").lower() == 'y':
            for gun in heat_guns:
                db.session.delete(gun)
            db.session.commit()
            print("Test tools removed")
        else:
            print("Test tools kept in database")

if __name__ == "__main__":
    test_duplicate_tool_numbers()
