#!/usr/bin/env python3
"""
Simple test server for E2E testing
Uses SQLite and minimal configuration
"""

import os
import sys
from flask import Flask
from flask_cors import CORS

# Set environment for testing
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'sqlite:///test_e2e.db'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, User, Tool, Chemical, UserActivity, AuditLog, Checkout
from routes_auth import register_auth_routes
from datetime import datetime, timedelta

def create_test_app():
    """Create a minimal Flask app for E2E testing"""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_e2e.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = False  # We want a real server, not test mode
    app.config['DEBUG'] = True
    
    # Enable CORS
    CORS(app, origins=['http://localhost:5173', 'http://localhost:3000'])
    
    # Initialize database
    db.init_app(app)
    
    # Register auth routes
    register_auth_routes(app)

    # Register additional API routes for testing
    register_test_api_routes(app)
    
    # Add basic health check
    @app.route('/health')
    def health():
        return {'status': 'ok', 'message': 'Test server running'}
    
    @app.route('/api/health')
    def api_health():
        return {'status': 'ok', 'message': 'API server running'}
    
    # Create tables and test data
    with app.app_context():
        db.create_all()

        # Create test users
        create_test_users()

        # Create test tools
        create_test_tools()

        # Create test chemicals
        create_test_chemicals()

        # Create test checkouts and activities
        create_test_activities()
    
    return app

def create_test_users():
    """Create test users with different roles"""
    users_data = [
        {
            'name': 'Test Admin',
            'employee_number': 'ADMIN001',
            'department': 'IT',
            'is_admin': True,
            'is_active': True,
            'password': 'admin123'
        },
        {
            'name': 'John Engineer',
            'employee_number': 'USER001',
            'department': 'Engineering',
            'is_admin': False,
            'is_active': True,
            'password': 'user123'
        },
        {
            'name': 'Sarah Materials',
            'employee_number': 'MAT001',
            'department': 'Materials',
            'is_admin': False,
            'is_active': True,
            'password': 'materials123'
        },
        {
            'name': 'Mike Quality',
            'employee_number': 'QA001',
            'department': 'Quality',
            'is_admin': False,
            'is_active': True,
            'password': 'quality123'
        },
        {
            'name': 'Lisa Production',
            'employee_number': 'PROD001',
            'department': 'Production',
            'is_admin': False,
            'is_active': True,
            'password': 'production123'
        }
    ]

    for user_data in users_data:
        existing_user = User.query.filter_by(employee_number=user_data['employee_number']).first()
        if not existing_user:
            user = User(
                name=user_data['name'],
                employee_number=user_data['employee_number'],
                department=user_data['department'],
                is_admin=user_data['is_admin'],
                is_active=user_data['is_active']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            print(f"Created user: {user_data['employee_number']} / {user_data['password']}")

    db.session.commit()

def create_test_tools():
    """Create test tools with various categories and statuses"""
    admin = User.query.filter_by(employee_number='ADMIN001').first()

    tools_data = [
        {
            'tool_number': 'T001',
            'serial_number': 'SN001',
            'description': 'Digital Multimeter',
            'condition': 'Excellent',
            'location': 'Tool Crib A-1',
            'category': 'Testing',
            'status': 'available',
            'requires_calibration': True,
            'calibration_frequency_days': 365
        },
        {
            'tool_number': 'T002',
            'serial_number': 'SN002',
            'description': 'Torque Wrench Set',
            'condition': 'Good',
            'location': 'Tool Crib A-2',
            'category': 'Hand Tools',
            'status': 'available',
            'requires_calibration': True,
            'calibration_frequency_days': 180
        },
        {
            'tool_number': 'T003',
            'serial_number': 'SN003',
            'description': 'Oscilloscope',
            'condition': 'Excellent',
            'location': 'Electronics Lab',
            'category': 'Testing',
            'status': 'checked_out',
            'requires_calibration': True,
            'calibration_frequency_days': 365
        },
        {
            'tool_number': 'T004',
            'serial_number': 'SN004',
            'description': 'Drill Press',
            'condition': 'Good',
            'location': 'Machine Shop',
            'category': 'Power Tools',
            'status': 'maintenance',
            'requires_calibration': False
        },
        {
            'tool_number': 'T005',
            'serial_number': 'SN005',
            'description': 'Micrometer Set',
            'condition': 'Excellent',
            'location': 'Quality Lab',
            'category': 'Measuring',
            'status': 'available',
            'requires_calibration': True,
            'calibration_frequency_days': 365
        }
    ]

    for tool_data in tools_data:
        existing_tool = Tool.query.filter_by(tool_number=tool_data['tool_number']).first()
        if not existing_tool:
            tool = Tool(
                tool_number=tool_data['tool_number'],
                serial_number=tool_data['serial_number'],
                description=tool_data['description'],
                condition=tool_data['condition'],
                location=tool_data['location'],
                category=tool_data['category'],
                status=tool_data['status'],
                requires_calibration=tool_data.get('requires_calibration', False),
                calibration_frequency_days=tool_data.get('calibration_frequency_days')
            )

            # Skip calibration setup for simplicity in testing
            # Calibration features can be tested separately

            db.session.add(tool)
            print(f"Created tool: {tool_data['tool_number']} - {tool_data['description']}")

    db.session.commit()

def create_test_chemicals():
    """Create test chemicals with various statuses"""
    admin = User.query.filter_by(employee_number='ADMIN001').first()

    chemicals_data = [
        {
            'part_number': 'C001',
            'lot_number': 'LOT001',
            'description': 'Isopropyl Alcohol 99%',
            'manufacturer': 'ChemCorp',
            'quantity': 500.0,
            'unit': 'ml',
            'location': 'Chemical Storage A-1',
            'category': 'Solvents',
            'status': 'available',
            'minimum_stock_level': 100.0
        },
        {
            'part_number': 'C002',
            'lot_number': 'LOT002',
            'description': 'Acetone Technical Grade',
            'manufacturer': 'ChemCorp',
            'quantity': 25.0,
            'unit': 'ml',
            'location': 'Chemical Storage A-2',
            'category': 'Solvents',
            'status': 'low_stock',
            'minimum_stock_level': 50.0
        },
        {
            'part_number': 'C003',
            'lot_number': 'LOT003',
            'description': 'Flux Paste',
            'manufacturer': 'SolderTech',
            'quantity': 200.0,
            'unit': 'g',
            'location': 'Electronics Lab',
            'category': 'Soldering',
            'status': 'available',
            'minimum_stock_level': 50.0
        }
    ]

    for chem_data in chemicals_data:
        existing_chemical = Chemical.query.filter_by(part_number=chem_data['part_number']).first()
        if not existing_chemical:
            chemical = Chemical(
                part_number=chem_data['part_number'],
                lot_number=chem_data['lot_number'],
                description=chem_data['description'],
                manufacturer=chem_data['manufacturer'],
                quantity=chem_data['quantity'],
                unit=chem_data['unit'],
                location=chem_data['location'],
                category=chem_data['category'],
                status=chem_data['status'],
                minimum_stock_level=chem_data['minimum_stock_level']
            )
            db.session.add(chemical)
            print(f"Created chemical: {chem_data['part_number']} - {chem_data['description']}")

    db.session.commit()

def create_test_activities():
    """Create test checkouts and user activities"""
    admin = User.query.filter_by(employee_number='ADMIN001').first()
    user = User.query.filter_by(employee_number='USER001').first()
    tool = Tool.query.filter_by(tool_number='T003').first()  # Oscilloscope

    if tool and user:
        # Create a checkout for the oscilloscope
        existing_checkout = Checkout.query.filter_by(tool_id=tool.id, return_date=None).first()
        if not existing_checkout:
            checkout = Checkout(
                tool_id=tool.id,
                user_id=user.id,
                checkout_date=datetime.now() - timedelta(days=2),
                expected_return_date=datetime.now() + timedelta(days=5)
            )
            db.session.add(checkout)

            # Update tool status
            tool.status = 'checked_out'

            print(f"Created checkout: {tool.tool_number} to {user.employee_number}")

    # Create some user activities
    activities_data = [
        {
            'user_id': admin.id,
            'activity_type': 'login',
            'description': 'Admin logged in',
            'timestamp': datetime.now() - timedelta(hours=1)
        },
        {
            'user_id': user.id,
            'activity_type': 'checkout',
            'description': f'Checked out tool {tool.tool_number}' if tool else 'Checked out tool',
            'timestamp': datetime.now() - timedelta(days=2)
        },
        {
            'user_id': admin.id,
            'activity_type': 'create',
            'description': 'Created new tool T005',
            'timestamp': datetime.now() - timedelta(days=1)
        }
    ]

    for activity_data in activities_data:
        activity = UserActivity(
            user_id=activity_data['user_id'],
            activity_type=activity_data['activity_type'],
            description=activity_data['description'],
            timestamp=activity_data['timestamp']
        )
        db.session.add(activity)

    db.session.commit()
    print("Created test activities and checkouts")

def register_test_api_routes(app):
    """Register basic API routes for testing"""

    @app.route('/api/tools', methods=['GET'])
    def get_tools():
        tools = Tool.query.all()
        return {'tools': [tool.to_dict() for tool in tools]}

    @app.route('/api/chemicals', methods=['GET'])
    def get_chemicals():
        chemicals = Chemical.query.all()
        return {'chemicals': [chemical.to_dict() for chemical in chemicals]}

    @app.route('/api/checkouts', methods=['GET'])
    def get_checkouts():
        checkouts = Checkout.query.all()
        return {'checkouts': [checkout.to_dict() for checkout in checkouts]}

    @app.route('/api/checkouts/user', methods=['GET'])
    def get_user_checkouts():
        # Return empty list for now
        return {'checkouts': []}

    @app.route('/api/user/activity', methods=['GET'])
    def get_user_activity():
        activities = UserActivity.query.limit(10).all()
        return {'activities': [activity.to_dict() for activity in activities]}

    # Add stub routes for other endpoints to prevent 404 errors
    @app.route('/api/calibrations/due', methods=['GET'])
    def calibrations_due():
        return {'data': [], 'message': 'Test endpoint - no data available'}

    @app.route('/api/calibrations/overdue', methods=['GET'])
    def calibrations_overdue():
        return {'data': [], 'message': 'Test endpoint - no data available'}

    @app.route('/api/checkouts/overdue', methods=['GET'])
    def checkouts_overdue():
        return {'data': [], 'message': 'Test endpoint - no data available'}

    @app.route('/api/chemicals/on-order', methods=['GET'])
    def chemicals_on_order():
        return {'data': [], 'message': 'Test endpoint - no data available'}

    @app.route('/api/chemicals/expiring-soon', methods=['GET'])
    def chemicals_expiring_soon():
        return {'data': [], 'message': 'Test endpoint - no data available'}

    @app.route('/api/chemicals/reorder-needed', methods=['GET'])
    def chemicals_reorder_needed():
        return {'data': [], 'message': 'Test endpoint - no data available'}

    @app.route('/api/announcements', methods=['GET'])
    def announcements():
        return {'data': [], 'message': 'Test endpoint - no data available'}

    @app.route('/api/calibrations', methods=['GET'])
    def calibrations():
        return {'data': [], 'message': 'Test endpoint - no data available'}

    @app.route('/api/calibration-standards', methods=['GET'])
    def calibration_standards():
        return {'data': [], 'message': 'Test endpoint - no data available'}

    @app.route('/api/cycle-counts/schedules', methods=['GET'])
    def cycle_counts_schedules():
        return {'data': [], 'message': 'Test endpoint - no data available'}

    @app.route('/api/cycle-counts/batches', methods=['GET'])
    def cycle_counts_batches():
        return {'data': [], 'message': 'Test endpoint - no data available'}

    @app.route('/api/cycle-counts/discrepancies', methods=['GET'])
    def cycle_counts_discrepancies():
        return {'data': [], 'message': 'Test endpoint - no data available'}

    @app.route('/api/cycle-counts/analytics', methods=['GET'])
    def cycle_counts_analytics():
        return {'data': [], 'message': 'Test endpoint - no data available'}

    @app.route('/api/cycle-counts/stats', methods=['GET'])
    def cycle_counts_stats():
        return {'data': [], 'message': 'Test endpoint - no data available'}

    @app.route('/api/reports/tools', methods=['GET'])
    def reports_tools():
        return {'data': [], 'message': 'Test endpoint - no data available'}

if __name__ == '__main__':
    app = create_test_app()
    print("Starting test server on http://localhost:5000")
    print("Test users:")
    print("  Admin: ADMIN001 / admin123")
    print("  User:  USER001 / user123")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
