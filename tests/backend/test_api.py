import pytest
import sys
import os
import json
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app import create_app
from models import db, Tool, User, Checkout, AuditLog
from config import Config

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = None


@pytest.fixture(scope='module')
def test_app():
    app = create_app()
    app.config.from_object(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture(scope='function')
def init_database(test_app):
    with test_app.app_context():
        db.session.query(Tool).delete()
        db.session.query(User).delete()
        db.session.query(Checkout).delete()
        db.session.query(AuditLog).delete()
        db.session.commit()


@pytest.fixture(scope='function')
def admin_user(test_app, init_database):
    """Create an admin user for testing"""
    with test_app.app_context():
        admin = User(
            name='Test Admin',
            employee_number='ADMIN001',
            department='IT',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        return admin


@pytest.fixture(scope='function')
def authenticated_client(test_client, admin_user):
    """Create an authenticated test client"""
    # Login as admin
    login_data = {
        'employee_number': 'ADMIN001',
        'password': 'admin123'
    }
    with test_client.session_transaction() as sess:
        # Clear any existing session data
        sess.clear()

    response = test_client.post('/api/auth/login', json=login_data)
    print(f"Login response status: {response.status_code}")
    print(f"Login response data: {response.get_json()}")
    assert response.status_code == 200
    return test_client

def test_create_tool(authenticated_client, init_database):
    tool_data = {
        'tool_number': 'T001',
        'serial_number': 'SN001',
        'description': 'Hammer',
        'condition': 'New',
        'location': 'Warehouse'
    }
    response = authenticated_client.post('/api/tools', json=tool_data)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data

    # Verify tool created in database
    with authenticated_client.application.app_context():
        tool = Tool.query.filter_by(id=data['id']).first()
        assert tool is not None
        assert tool.tool_number == 'T001'

def test_get_tools(authenticated_client, init_database):
    tool1 = Tool(tool_number='T001', serial_number='SN001', description='Hammer', condition='New', location='Warehouse')
    tool2 = Tool(tool_number='T002', serial_number='SN002', description='Drill', condition='Used', location='Shelf')
    with authenticated_client.application.app_context():
        db.session.add_all([tool1, tool2])
        db.session.commit()

    response = authenticated_client.get('/api/tools')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) >= 2  # May have more tools from other tests
    # Check that our tools are in the response
    tool_numbers = [tool['tool_number'] for tool in data]
    assert 'T001' in tool_numbers
    assert 'T002' in tool_numbers

def test_authentication_flow(test_client, admin_user):
    """Test the authentication flow"""
    # Test login
    login_data = {
        'employee_number': 'ADMIN001',
        'password': 'admin123'
    }
    response = test_client.post('/api/auth/login', json=login_data)
    assert response.status_code == 200
    data = json.loads(response.data)

    # Check if login was successful - response contains user data directly
    assert 'token' in data
    assert data['employee_number'] == 'ADMIN001'
    assert data['is_admin'] is True

    # Test session info
    response = test_client.get('/api/auth/session-info')
    assert response.status_code == 200
    data = json.loads(response.data)

    # Check if user is authenticated
    assert data.get('authenticated', False) is True

def test_database_models(test_app, init_database):
    """Test basic database model functionality"""
    with test_app.app_context():
        # Test Tool model
        tool = Tool(
            tool_number='T001',
            serial_number='SN001',
            description='Test Hammer',
            condition='New',
            location='Warehouse'
        )
        db.session.add(tool)
        db.session.commit()

        # Verify tool was created
        saved_tool = Tool.query.filter_by(tool_number='T001').first()
        assert saved_tool is not None
        assert saved_tool.description == 'Test Hammer'

        # Test User model
        user = User(
            name='Test User',
            employee_number='TEST001',
            department='Testing'
        )
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()

        # Verify user was created and password works
        saved_user = User.query.filter_by(employee_number='TEST001').first()
        assert saved_user is not None
        assert saved_user.check_password('testpass') is True
        assert saved_user.check_password('wrongpass') is False


def test_api_health_check(test_client):
    """Test basic API health check"""
    response = test_client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data