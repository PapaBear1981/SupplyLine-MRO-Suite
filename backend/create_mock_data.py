#!/usr/bin/env python3
"""
Mock Data Creation Script for SupplyLine MRO Suite

This script creates comprehensive mock data for testing all features of the application:
- Users (admin, regular users, different departments)
- Tools (various categories, conditions, calibration requirements)
- Chemicals (different types, quantities, locations)
- Checkouts (active and historical)
- Calibration records
- Cycle count data
- User activities and audit logs

Usage:
    python create_mock_data.py [environment]

Where environment is one of: development, production (default: development)
"""

import logging
import os
import random
import sys
from datetime import UTC, datetime, timedelta

from flask import Flask

from config import Config
from models import CalibrationStandard, Checkout, Chemical, Tool, ToolCalibration, User, UserActivity, db


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_current_time():
    """Get current UTC time"""
    return datetime.now(UTC)


def create_mock_users():
    """Create mock users for different departments and roles"""
    logger.info("Creating mock users...")

    users_data = [
        {
            "name": "John Smith",
            "employee_number": "MAINT001",
            "department": "Maintenance",
            "password": "password123",
            "is_admin": False
        },
        {
            "name": "Sarah Johnson",
            "employee_number": "MAINT002",
            "department": "Maintenance",
            "password": "password123",
            "is_admin": False
        },
        {
            "name": "Mike Wilson",
            "employee_number": "PROD001",
            "department": "Production",
            "password": "password123",
            "is_admin": False
        },
        {
            "name": "Lisa Chen",
            "employee_number": "QC001",
            "department": "Quality Control",
            "password": "password123",
            "is_admin": False
        },
        {
            "name": "David Brown",
            "employee_number": "ENG001",
            "department": "Engineering",
            "password": "password123",
            "is_admin": False
        },
        {
            "name": "Jennifer Davis",
            "employee_number": "SUPER001",
            "department": "Maintenance",
            "password": "password123",
            "is_admin": True
        }
    ]

    created_users = []
    for user_data in users_data:
        # Check if user already exists
        existing_user = User.query.filter_by(employee_number=user_data["employee_number"]).first()
        if existing_user:
            logger.info(f"User {user_data['employee_number']} already exists, skipping...")
            created_users.append(existing_user)
            continue

        user = User(
            name=user_data["name"],
            employee_number=user_data["employee_number"],
            department=user_data["department"],
            is_admin=user_data["is_admin"],
            is_active=True,
            created_at=get_current_time()
        )
        user.set_password(user_data["password"])

        db.session.add(user)
        created_users.append(user)
        logger.info(f"Created user: {user.name} ({user.employee_number})")

    db.session.commit()
    return created_users


def create_mock_tools():
    """Create mock tools with various categories and conditions"""
    logger.info("Creating mock tools...")

    # Get admin user for created_by field
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        logger.error("No admin user found. Please run db_init.py first.")
        return []

    tools_data = [
        {
            "tool_number": "DMM001",
            "serial_number": "FL87V-001",
            "description": "Fluke 87V Digital Multimeter",
            "condition": "Excellent",
            "location": "Tool Crib A-1",
            "category": "Testing Equipment",
            "status": "available",
            "requires_calibration": True,
            "calibration_frequency_days": 365
        },
        {
            "tool_number": "TW001",
            "serial_number": "TW-85-001",
            "description": 'Torque Wrench 1/2" Drive 30-250 ft-lbs',
            "condition": "Good",
            "location": "Tool Crib A-2",
            "category": "Hand Tools",
            "status": "available",
            "requires_calibration": True,
            "calibration_frequency_days": 180
        },
        {
            "tool_number": "OSC001",
            "serial_number": "TEK-2000-001",
            "description": "Tektronix Digital Oscilloscope 100MHz",
            "condition": "Excellent",
            "location": "Electronics Lab",
            "category": "Testing Equipment",
            "status": "checked_out",
            "requires_calibration": True,
            "calibration_frequency_days": 365
        },
        {
            "tool_number": "IMP001",
            "serial_number": "IR-001",
            "description": 'Pneumatic Impact Wrench 1/2"',
            "condition": "Good",
            "location": "Shop Floor Station 3",
            "category": "Power Tools",
            "status": "available",
            "requires_calibration": False
        },
        {
            "tool_number": "MIC001",
            "serial_number": "MIT-001",
            "description": 'Mitutoyo Digital Micrometer 0-1"',
            "condition": "Excellent",
            "location": "Quality Lab",
            "category": "Measuring Tools",
            "status": "available",
            "requires_calibration": True,
            "calibration_frequency_days": 365
        }
    ]

    created_tools = []
    for tool_data in tools_data:
        # Check if tool already exists
        existing_tool = Tool.query.filter_by(tool_number=tool_data["tool_number"]).first()
        if existing_tool:
            logger.info(f"Tool {tool_data['tool_number']} already exists, skipping...")
            created_tools.append(existing_tool)
            continue

        tool = Tool(
            tool_number=tool_data["tool_number"],
            serial_number=tool_data["serial_number"],
            description=tool_data["description"],
            condition=tool_data["condition"],
            location=tool_data["location"],
            category=tool_data["category"],
            status=tool_data["status"],
            requires_calibration=tool_data["requires_calibration"],
            calibration_frequency_days=tool_data.get("calibration_frequency_days"),
            created_at=get_current_time()
        )

        db.session.add(tool)
        created_tools.append(tool)
        logger.info(f"Created tool: {tool.tool_number} - {tool.description}")

    db.session.commit()
    return created_tools


def create_mock_chemicals():
    """Create mock chemicals with various categories and quantities"""
    logger.info("Creating mock chemicals...")

    # Get admin user for created_by field
    User.query.filter_by(is_admin=True).first()

    chemicals_data = [
        {
            "part_number": "SEAL001",
            "lot_number": "L2024001",
            "description": "RTV Silicone Sealant Clear",
            "manufacturer": "Dow Corning",
            "quantity": 24.0,
            "unit": "tubes",
            "location": "Chemical Storage A-1",
            "category": "Sealants",
            "status": "available",
            "minimum_stock_level": 5.0
        },
        {
            "part_number": "PAINT001",
            "lot_number": "L2024002",
            "description": "Primer Paint Gray",
            "manufacturer": "Sherwin Williams",
            "quantity": 8.5,
            "unit": "gallons",
            "location": "Paint Storage B-2",
            "category": "Paints",
            "status": "available",
            "minimum_stock_level": 2.0
        },
        {
            "part_number": "CLEAN001",
            "lot_number": "L2024003",
            "description": "Degreaser Industrial Strength",
            "manufacturer": "Simple Green",
            "quantity": 12.0,
            "unit": "gallons",
            "location": "Chemical Storage A-3",
            "category": "Cleaners",
            "status": "available",
            "minimum_stock_level": 3.0
        },
        {
            "part_number": "ADHES001",
            "lot_number": "L2024004",
            "description": "Epoxy Adhesive 2-Part",
            "manufacturer": "3M",
            "quantity": 2.0,
            "unit": "kits",
            "location": "Chemical Storage A-1",
            "category": "Adhesives",
            "status": "low_stock",
            "minimum_stock_level": 3.0
        }
    ]

    created_chemicals = []
    for chem_data in chemicals_data:
        # Check if chemical already exists
        existing_chem = Chemical.query.filter_by(
            part_number=chem_data["part_number"],
            lot_number=chem_data["lot_number"]
        ).first()
        if existing_chem:
            logger.info(f"Chemical {chem_data['part_number']} already exists, skipping...")
            created_chemicals.append(existing_chem)
            continue

        chemical = Chemical(
            part_number=chem_data["part_number"],
            lot_number=chem_data["lot_number"],
            description=chem_data["description"],
            manufacturer=chem_data["manufacturer"],
            quantity=chem_data["quantity"],
            unit=chem_data["unit"],
            location=chem_data["location"],
            category=chem_data["category"],
            status=chem_data["status"],
            minimum_stock_level=chem_data.get("minimum_stock_level"),
            date_added=get_current_time()
        )

        db.session.add(chemical)
        created_chemicals.append(chemical)
        logger.info(f"Created chemical: {chemical.part_number} - {chemical.description}")

    db.session.commit()
    return created_chemicals


def create_mock_checkouts(users, tools):
    """Create mock checkouts (active and historical)"""
    logger.info("Creating mock checkouts...")

    if not users or not tools:
        logger.warning("No users or tools available for creating checkouts")
        return []

    # Create some active checkouts
    active_checkouts = [
        {
            "tool": next((t for t in tools if t.tool_number == "OSC001"), None),
            "user": next((u for u in users if u.employee_number == "ENG001"), None),
            "days_ago": 3,
            "expected_return_days": 7
        }
    ]

    # Create some historical checkouts (returned)
    historical_checkouts = [
        {
            "tool": next((t for t in tools if t.tool_number == "DMM001"), None),
            "user": next((u for u in users if u.employee_number == "MAINT001"), None),
            "checkout_days_ago": 10,
            "return_days_ago": 5,
            "expected_return_days": 7
        },
        {
            "tool": next((t for t in tools if t.tool_number == "TW001"), None),
            "user": next((u for u in users if u.employee_number == "MAINT002"), None),
            "checkout_days_ago": 15,
            "return_days_ago": 12,
            "expected_return_days": 14
        }
    ]

    created_checkouts = []

    # Create active checkouts
    for checkout_data in active_checkouts:
        if not checkout_data["tool"] or not checkout_data["user"]:
            continue

        # Check if checkout already exists
        existing_checkout = Checkout.query.filter_by(
            tool_id=checkout_data["tool"].id,
            return_date=None
        ).first()
        if existing_checkout:
            logger.info(f"Active checkout for {checkout_data['tool'].tool_number} already exists")
            created_checkouts.append(existing_checkout)
            continue

        checkout = Checkout(
            tool_id=checkout_data["tool"].id,
            user_id=checkout_data["user"].id,
            checkout_date=get_current_time() - timedelta(days=checkout_data["days_ago"]),
            expected_return_date=get_current_time() + timedelta(days=checkout_data["expected_return_days"])
        )

        db.session.add(checkout)
        created_checkouts.append(checkout)

        # Update tool status
        checkout_data["tool"].status = "checked_out"

        logger.info(f"Created active checkout: {checkout_data['tool'].tool_number} to {checkout_data['user'].employee_number}")

    # Create historical checkouts
    for checkout_data in historical_checkouts:
        if not checkout_data["tool"] or not checkout_data["user"]:
            continue

        checkout = Checkout(
            tool_id=checkout_data["tool"].id,
            user_id=checkout_data["user"].id,
            checkout_date=get_current_time() - timedelta(days=checkout_data["checkout_days_ago"]),
            return_date=get_current_time() - timedelta(days=checkout_data["return_days_ago"]),
            expected_return_date=get_current_time() - timedelta(days=checkout_data["checkout_days_ago"] - checkout_data["expected_return_days"])
        )

        db.session.add(checkout)
        created_checkouts.append(checkout)

        logger.info(f"Created historical checkout: {checkout_data['tool'].tool_number} by {checkout_data['user'].employee_number}")

    db.session.commit()
    return created_checkouts


def create_mock_calibration_data(tools):
    """Create mock calibration standards and records"""
    logger.info("Creating mock calibration data...")

    if not tools:
        logger.warning("No tools available for creating calibration data")
        return

    # Create calibration standards
    standards_data = [
        {
            "name": "Voltage Standard 10V",
            "description": "Precision voltage reference 10.000V ±0.001%",
            "standard_number": "VS-10V-001",
            "certification_date": get_current_time() - timedelta(days=90),
            "expiration_date": get_current_time() + timedelta(days=275)
        },
        {
            "name": "Torque Standard 100 ft-lbs",
            "description": "Torque calibration standard 100 ft-lbs",
            "standard_number": "TS-100-001",
            "certification_date": get_current_time() - timedelta(days=60),
            "expiration_date": get_current_time() + timedelta(days=120)
        }
    ]

    created_standards = []
    for std_data in standards_data:
        # Check if standard already exists
        existing_std = CalibrationStandard.query.filter_by(standard_number=std_data["standard_number"]).first()
        if existing_std:
            logger.info(f"Calibration standard {std_data['standard_number']} already exists")
            created_standards.append(existing_std)
            continue

        standard = CalibrationStandard(
            name=std_data["name"],
            description=std_data["description"],
            standard_number=std_data["standard_number"],
            certification_date=std_data["certification_date"],
            expiration_date=std_data["expiration_date"],
            created_at=get_current_time()
        )

        db.session.add(standard)
        created_standards.append(standard)
        logger.info(f"Created calibration standard: {standard.name}")

    db.session.commit()

    # Create tool calibration records
    calibration_tools = [t for t in tools if t.requires_calibration]
    admin = User.query.filter_by(is_admin=True).first()

    for tool in calibration_tools[:3]:  # Create calibrations for first 3 tools
        # Check if calibration already exists
        existing_cal = ToolCalibration.query.filter_by(tool_id=tool.id).first()
        if existing_cal:
            logger.info(f"Calibration for {tool.tool_number} already exists")
            continue

        calibration = ToolCalibration(
            tool_id=tool.id,
            calibration_date=get_current_time() - timedelta(days=random.randint(30, 180)),
            next_calibration_date=get_current_time() + timedelta(days=random.randint(180, 365)),
            performed_by_user_id=admin.id,
            calibration_status="completed",
            calibration_notes="Calibration performed according to manufacturer specifications",
            created_at=get_current_time()
        )

        db.session.add(calibration)
        logger.info(f"Created calibration record for: {tool.tool_number}")

    db.session.commit()


def create_mock_user_activities(users, tools, chemicals):
    """Create mock user activities and audit logs"""
    logger.info("Creating mock user activities...")

    if not users:
        logger.warning("No users available for creating activities")
        return

    # Create various user activities
    activities = [
        {
            "user": next((u for u in users if u.employee_number == "MAINT001"), None),
            "activity_type": "login",
            "description": "User logged in",
            "days_ago": 1
        },
        {
            "user": next((u for u in users if u.employee_number == "MAINT001"), None),
            "activity_type": "tool_search",
            "description": "Searched for multimeter tools",
            "days_ago": 1
        },
        {
            "user": next((u for u in users if u.employee_number == "ENG001"), None),
            "activity_type": "checkout",
            "description": "Checked out oscilloscope OSC001",
            "days_ago": 3
        }
    ]

    for activity_data in activities:
        if not activity_data["user"]:
            continue

        activity = UserActivity(
            user_id=activity_data["user"].id,
            activity_type=activity_data["activity_type"],
            description=activity_data["description"],
            timestamp=get_current_time() - timedelta(days=activity_data["days_ago"])
        )

        db.session.add(activity)
        logger.info(f"Created activity: {activity_data['description']}")

    db.session.commit()


def main():
    """Main function to create all mock data"""
    try:
        # Get config from environment or use development
        config_name = os.environ.get("FLASK_ENV", "development")

        # Create Flask app
        app = Flask(__name__)
        app.config.from_object(Config)

        # Initialize database
        db.init_app(app)

        with app.app_context():
            logger.info(f"Creating mock data with config: {config_name}")

            # Ensure tables exist
            db.create_all()

            # Create mock data
            users = create_mock_users()
            tools = create_mock_tools()
            chemicals = create_mock_chemicals()
            checkouts = create_mock_checkouts(users, tools)
            create_mock_calibration_data(tools)
            create_mock_user_activities(users, tools, chemicals)

            logger.info("Mock data creation completed successfully!")
            logger.info("=" * 60)
            logger.info("MOCK DATA SUMMARY:")
            logger.info(f"Users created: {len(users)}")
            logger.info(f"Tools created: {len(tools)}")
            logger.info(f"Chemicals created: {len(chemicals)}")
            logger.info(f"Checkouts created: {len(checkouts)}")
            logger.info("=" * 60)
            logger.info("Test Login Credentials:")
            logger.info("Admin: ADMIN001 / admin123")
            logger.info("Maintenance: MAINT001 / password123")
            logger.info("Engineering: ENG001 / password123")
            logger.info("Quality Control: QC001 / password123")
            logger.info("=" * 60)

            return True

    except Exception as e:
        logger.error(f"Mock data creation failed: {e!s}")
        return False


if __name__ == "__main__":
    if main():
        logger.info("Mock data creation completed successfully!")
        sys.exit(0)
    else:
        logger.error("Mock data creation failed!")
        sys.exit(1)
