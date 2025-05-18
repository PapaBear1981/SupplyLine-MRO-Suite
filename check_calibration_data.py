from flask import Flask
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models import db, Tool
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/tools.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # Check if there are any tools that require calibration
    tools_requiring_calibration = Tool.query.filter_by(requires_calibration=True).all()
    print(f"Tools requiring calibration: {len(tools_requiring_calibration)}")

    for tool in tools_requiring_calibration:
        print(f"Tool ID: {tool.id}, Tool Number: {tool.tool_number}, Next Calibration Date: {tool.next_calibration_date}")

    # Check if there are any tools due for calibration in the next 30 days
    now = datetime.utcnow()
    threshold_date = now + timedelta(days=30)

    tools_due = Tool.query.filter(
        Tool.requires_calibration == True,
        Tool.next_calibration_date.isnot(None),
        Tool.next_calibration_date <= threshold_date,
        Tool.next_calibration_date >= now
    ).all()

    print(f"\nTools due for calibration in the next 30 days: {len(tools_due)}")

    for tool in tools_due:
        print(f"Tool ID: {tool.id}, Tool Number: {tool.tool_number}, Next Calibration Date: {tool.next_calibration_date}")

    # We'll skip checking calibration records for now since ToolCalibration might not be imported correctly
    print("\nSkipping calibration records check")
