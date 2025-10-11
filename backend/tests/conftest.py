"""
Test configuration and fixtures for SupplyLine MRO Suite tests
"""

import os
import sys
import tempfile
from datetime import datetime

import pytest

# Add the backend directory to the Python path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Lazily imported globals populated once we configure the environment
create_app = None
db = None
User = None
Tool = None
Chemical = None
UserActivity = None
AuditLog = None
JWTManager = None

@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    db_fd, db_path = tempfile.mkstemp()

    original_db_url = os.environ.get('DATABASE_URL')
    original_flask_env = os.environ.get('FLASK_ENV')
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
    os.environ['FLASK_ENV'] = 'testing'
    original_session_type = os.environ.get('SESSION_TYPE')
    os.environ['SESSION_TYPE'] = 'filesystem'

    try:
        global create_app, db, User, Tool, Chemical, UserActivity, AuditLog, JWTManager
        if create_app is None:
            from app import create_app as _create_app
            from models import (
                AuditLog as _AuditLog,
                Chemical as _Chemical,
                Tool as _Tool,
                User as _User,
                UserActivity as _UserActivity,
                db as _db,
            )
            from auth import JWTManager as _JWTManager

            create_app = _create_app
            db = _db
            User = _User
            Tool = _Tool
            Chemical = _Chemical
            UserActivity = _UserActivity
            AuditLog = _AuditLog
            JWTManager = _JWTManager

        application = create_app()

        # Test database configuration
        application.config.update({
            'DATABASE_URL': f'sqlite:///{db_path}',
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key',
            'JWT_SECRET_KEY': 'test-jwt-secret-key',
            'RATE_LIMITS': {},
            'SESSION_TYPE': 'filesystem',
        })

        yield application
    finally:
        if original_db_url is not None:
            os.environ['DATABASE_URL'] = original_db_url
        else:
            os.environ.pop('DATABASE_URL', None)

        if original_flask_env is not None:
            os.environ['FLASK_ENV'] = original_flask_env
        else:
            os.environ.pop('FLASK_ENV', None)

        if original_session_type is not None:
            os.environ['SESSION_TYPE'] = original_session_type
        else:
            os.environ.pop('SESSION_TYPE', None)

        os.close(db_fd)
        os.unlink(db_path)

@pytest.fixture(scope='session')
def _db(app):
    """Create database for testing"""
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture(scope='function')
def db_session(app, _db):
    """Create a fresh database session for each test"""
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        
        # Configure session to use the connection
        _db.session.configure(bind=connection)
        
        yield _db.session
        
        # Rollback transaction and close connection
        transaction.rollback()
        connection.close()
        _db.session.remove()

@pytest.fixture
def client(app, db_session):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def jwt_manager(app):
    """Create JWT manager for testing"""
    return JWTManager(app)

@pytest.fixture
def admin_user(db_session):
    """Create admin user for testing"""
    user = User(
        name='Test Admin',
        employee_number='ADMIN001',
        department='IT',
        is_admin=True,
        is_active=True
    )
    user.set_password('admin123')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def regular_user(db_session):
    """Create regular user for testing"""
    existing = User.query.filter_by(employee_number='USER001').first()
    if existing:
        db_session.delete(existing)
        db_session.flush()

    user = User(
        name='Test User',
        employee_number='USER001',
        department='Engineering',
        is_admin=False,
        is_active=True
    )
    user.set_password('user123')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def sample_tool(db_session, admin_user):
    """Create sample tool for testing"""
    tool = Tool(
        tool_number='T001',
        serial_number='S001',
        description='Test Tool',
        condition='Good',
        location='Test Location',
        category='Testing',
        status='available',
        created_by=admin_user.id,
        created_at=datetime.utcnow()
    )
    db_session.add(tool)
    db_session.commit()
    return tool

@pytest.fixture
def sample_chemical(db_session, admin_user):
    """Create sample chemical for testing"""
    chemical = Chemical(
        part_number='C001',
        lot_number='L001',
        description='Test Chemical',
        manufacturer='Test Manufacturer',
        quantity=100.0,
        unit='ml',
        location='Test Location',
        category='Testing',
        status='available',
        created_by=admin_user.id,
        created_at=datetime.utcnow()
    )
    db_session.add(chemical)
    db_session.commit()
    return chemical

@pytest.fixture
def auth_headers(client, admin_user, jwt_manager):
    """Get authentication headers for admin user"""
    with client.application.app_context():
        tokens = jwt_manager.generate_tokens(admin_user)
    access_token = tokens['access_token']
    return {'Authorization': f'Bearer {access_token}'}

@pytest.fixture
def user_auth_headers(client, regular_user, jwt_manager):
    """Get authentication headers for regular user"""
    with client.application.app_context():
        tokens = jwt_manager.generate_tokens(regular_user)
    access_token = tokens['access_token']
    return {'Authorization': f'Bearer {access_token}'}

@pytest.fixture
def sample_data(db_session, admin_user, regular_user):
    """Create comprehensive sample data for testing"""
    # Create additional tools
    tools = []
    for i in range(5):
        tool = Tool(
            tool_number=f'T{i+2:03d}',
            serial_number=f'S{i+2:03d}',
            description=f'Test Tool {i+2}',
            condition='Good',
            location=f'Location {i+1}',
            category='Testing',
            status='available',
            created_by=admin_user.id,
            created_at=datetime.utcnow()
        )
        tools.append(tool)
        db_session.add(tool)
    
    # Create additional chemicals
    chemicals = []
    for i in range(3):
        chemical = Chemical(
            part_number=f'C{i+2:03d}',
            lot_number=f'L{i+2:03d}',
            description=f'Test Chemical {i+2}',
            manufacturer='Test Manufacturer',
            quantity=50.0 + (i * 25),
            unit='ml',
            location=f'Chemical Storage {i+1}',
            category='Testing',
            status='available',
            created_by=admin_user.id,
            created_at=datetime.utcnow()
        )
        chemicals.append(chemical)
        db_session.add(chemical)
    
    # Create some user activities
    activities = []
    for i, tool in enumerate(tools[:2]):
        activity = UserActivity(
            user_id=regular_user.id,
            activity_type='checkout',
            description=f'Checked out {tool.tool_number}',
            timestamp=datetime.utcnow()
        )
        activities.append(activity)
        db_session.add(activity)
    
    db_session.commit()
    
    return {
        'tools': tools,
        'chemicals': chemicals,
        'activities': activities
    }

# Test utilities
class TestUtils:
    """Utility functions for testing"""
    
    @staticmethod
    def assert_json_response(response, expected_status=200):
        """Assert that response is JSON with expected status"""
        assert response.status_code == expected_status
        assert response.content_type == 'application/json'
        return response.get_json()
    
    @staticmethod
    def assert_error_response(response, expected_status=400):
        """Assert that response is an error with expected status"""
        assert response.status_code == expected_status
        data = response.get_json()
        assert 'error' in data
        return data
    
    @staticmethod
    def create_test_user(db_session, employee_number, name="Test User", is_admin=False):
        """Create a test user"""
        user = User(
            name=name,
            employee_number=employee_number,
            department='Testing',
            is_admin=is_admin,
            is_active=True
        )
        user.set_password('test123')
        db_session.add(user)
        db_session.commit()
        return user

@pytest.fixture
def test_utils():
    """Provide test utilities"""
    return TestUtils
