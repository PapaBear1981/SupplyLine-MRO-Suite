from backend.app import app, db
from backend.models import Tool

with app.app_context():
    tool = Tool(
        tool_number='T001',
        serial_number='S001',
        description='Test Tool',
        condition='Good',
        location='Storage',
        category='General'
    )
    db.session.add(tool)
    db.session.commit()
    print('Tool added successfully')
