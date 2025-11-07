"""
Test configuration and fixtures for SupplyLine MRO Suite tests
"""

import os
import sys
import tempfile
from datetime import datetime

import pytest
from sqlalchemy import text


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
Permission = None
Role = None
RolePermission = None
UserRole = None
JWTManager = None

@pytest.fixture(scope="session")
def app():
    """Create application for testing"""
    # B108 Mitigation: Use mkstemp for secure temporary file creation (avoids mktemp race condition).
    # File descriptor (db_fd) is closed and file (db_path) is unlinked in the 'finally' block.
    db_fd, db_path = tempfile.mkstemp()

    original_db_url = os.environ.get("DATABASE_URL")
    original_flask_env = os.environ.get("FLASK_ENV")
    original_session_type = os.environ.get("SESSION_TYPE")
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["FLASK_ENV"] = "testing"
    os.environ["SESSION_TYPE"] = "filesystem"

    try:
        global create_app, db, User, Tool, Chemical, UserActivity, AuditLog, JWTManager
        global Permission, Role, RolePermission, UserRole
        if create_app is None:
            from app import create_app as _create_app
            from auth import JWTManager as _JWTManager
            from models import (
                AuditLog as _AuditLog,
            )
            from models import (
                Chemical as _Chemical,
            )
            from models import (
                Tool as _Tool,
            )
            from models import (
                User as _User,
            )
            from models import (
                UserActivity as _UserActivity,
            )
            from models import (
                Permission as _Permission,
            )
            from models import (
                Role as _Role,
            )
            from models import (
                RolePermission as _RolePermission,
            )
            from models import (
                UserRole as _UserRole,
            )
            from models import (
                db as _db,
            )

            create_app = _create_app
            db = _db
            User = _User
            Tool = _Tool
            Chemical = _Chemical
            UserActivity = _UserActivity
            AuditLog = _AuditLog
            JWTManager = _JWTManager
            Permission = _Permission
            Role = _Role
            RolePermission = _RolePermission
            UserRole = _UserRole

        application = create_app()

        # Test database configuration
        application.config.update({
            "DATABASE_URL": f"sqlite:///{db_path}",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
            "JWT_SECRET_KEY": "test-jwt-secret-key",
            "RATE_LIMITS": {},
            "SESSION_TYPE": "filesystem",
        })

        yield application
    finally:
        if original_db_url is not None:
            os.environ["DATABASE_URL"] = original_db_url
        else:
            os.environ.pop("DATABASE_URL", None)

        if original_flask_env is not None:
            os.environ["FLASK_ENV"] = original_flask_env
        else:
            os.environ.pop("FLASK_ENV", None)

        if original_session_type is not None:
            os.environ["SESSION_TYPE"] = original_session_type
        else:
            os.environ.pop("SESSION_TYPE", None)

        os.close(db_fd)
        os.unlink(db_path)

@pytest.fixture(scope="session")
def _db(app):
    """Create database for testing"""
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture
def db_session(app, _db):
    """Provide a clean database session for each test."""
    with app.app_context():
        try:
            yield _db.session
        finally:
            # Ensure the session itself is in a clean state before truncation.
            _db.session.rollback()

            # Use a dedicated transaction to wipe all tables so that data
            # created in one test never bleeds into the next one.
            engine = _db.engine
            with engine.begin() as connection:
                if engine.dialect.name == "sqlite":
                    connection.execute(text("PRAGMA foreign_keys = OFF"))

                for table in reversed(_db.metadata.sorted_tables):
                    connection.execute(table.delete())

                if engine.dialect.name == "sqlite":
                    connection.execute(text("PRAGMA foreign_keys = ON"))

            _db.session.remove()

@pytest.fixture
def client(app, db_session):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def jwt_manager(app):
    """Create JWT manager for testing"""
    return JWTManager

@pytest.fixture
def admin_user(db_session):
    """Create admin user for testing"""
    # Use ADMIN001 to match backend/conftest.py and avoid conflicts
    # Delete any existing admin user (in case app initialization created one)
    existing = User.query.filter_by(employee_number="ADMIN001").first()
    if existing:
        db_session.delete(existing)
        db_session.commit()

    user = User(
        name="Test Admin",
        employee_number="ADMIN001",
        department="IT",
        is_admin=True,
        is_active=True
    )
    user.set_password("admin123")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_user(db_session):
    """Alias for regular_user to support tests that use test_user fixture"""
    # Delete any existing user to ensure clean state
    existing = User.query.filter_by(employee_number="USER001").first()
    if existing:
        db_session.delete(existing)
        db_session.commit()

    user = User(
        name="Test User",
        employee_number="USER001",
        department="Engineering",
        is_admin=False,
        is_active=True
    )
    user.set_password("user123")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def regular_user(db_session):
    """Create regular user for testing"""
    existing = User.query.filter_by(employee_number="USER001").first()
    if existing:
        db_session.delete(existing)
        db_session.flush()

    user = User(
        name="Test User",
        employee_number="USER001",
        department="Engineering",
        is_admin=False,
        is_active=True
    )
    user.set_password("user123")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_warehouse(db_session):
    """Create test warehouse for testing"""
    from models import Warehouse
    existing = Warehouse.query.filter_by(name="Test Warehouse").first()
    if existing:
        return existing

    warehouse = Warehouse(
        name="Test Warehouse",
        address="123 Test St",
        is_active=True
    )
    db_session.add(warehouse)
    db_session.commit()
    return warehouse

@pytest.fixture
def sample_tool(db_session, admin_user, test_warehouse):
    """Create sample tool for testing"""
    tool = Tool(
        tool_number="T001",
        serial_number="S001",
        description="Test Tool",
        condition="Good",
        location="Test Location",
        category="Testing",
        warehouse_id=test_warehouse.id,
        status="available"
    )
    db_session.add(tool)
    db_session.commit()
    return tool

@pytest.fixture
def sample_chemical(db_session, admin_user, test_warehouse):
    """Create sample chemical for testing"""
    chemical = Chemical(
        part_number="C001",
        lot_number="L001",
        description="Test Chemical",
        manufacturer="Test Manufacturer",
        quantity=100,
        unit="ml",
        location="Test Location",
        category="Testing",
        status="available",
        warehouse_id=test_warehouse.id,
    )
    db_session.add(chemical)
    db_session.commit()
    return chemical

@pytest.fixture
def auth_headers(client, admin_user, jwt_manager):
    """Get authentication headers for admin user"""
    with client.application.app_context():
        tokens = jwt_manager.generate_tokens(admin_user)
    access_token = tokens["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def user_auth_headers(client, regular_user, jwt_manager):
    """Get authentication headers for regular user"""
    with client.application.app_context():
        tokens = jwt_manager.generate_tokens(regular_user)
    access_token = tokens["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def materials_user(db_session):
    """Create a Materials department user"""
    import uuid
    emp_number = f"MAT{uuid.uuid4().hex[:6]}"

    user = User(
        name="Materials User",
        employee_number=emp_number,
        department="Materials",
        is_admin=False,
        is_active=True
    )
    user.set_password("materials123")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def auth_headers_materials(client, materials_user, jwt_manager):
    """Get auth headers for Materials user"""
    with client.application.app_context():
        tokens = jwt_manager.generate_tokens(materials_user)
    access_token = tokens["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def auth_headers_return_manager(client, db_session, regular_user, jwt_manager):
    """Get auth headers for a user with explicit tool return permission."""

    permission = db_session.query(Permission).filter_by(name="tool.return").first()
    if not permission:
        permission = Permission(name="tool.return", description="Return tools", category="Tool Management")
        db_session.add(permission)
        db_session.flush()

    role = db_session.query(Role).filter_by(name="Return Manager").first()
    if not role:
        role = Role(name="Return Manager", description="Can process tool returns")
        db_session.add(role)
        db_session.flush()

    role_permission = (
        db_session.query(RolePermission)
        .filter_by(role_id=role.id, permission_id=permission.id)
        .first()
    )
    if not role_permission:
        role_permission = RolePermission(role_id=role.id, permission_id=permission.id)
        db_session.add(role_permission)

    user_role = db_session.query(UserRole).filter_by(user_id=regular_user.id, role_id=role.id).first()
    if not user_role:
        user_role = UserRole(user_id=regular_user.id, role_id=role.id)
        db_session.add(user_role)

    db_session.commit()

    with client.application.app_context():
        tokens = jwt_manager.generate_tokens(regular_user)
    access_token = tokens["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def sample_data(db_session, admin_user, regular_user):
    """Create comprehensive sample data for testing"""
    # Create additional tools
    tools = []
    for i in range(5):
        tool = Tool(
            tool_number=f"T{i+2:03d}",
            serial_number=f"S{i+2:03d}",
            description=f"Test Tool {i+2}",
            condition="Good",
            location=f"Location {i+1}",
            category="Testing",
            status="available",
            created_by=admin_user.id,
            created_at=datetime.utcnow()
        )
        tools.append(tool)
        db_session.add(tool)

    # Create additional chemicals
    chemicals = []
    for i in range(3):
        chemical = Chemical(
            part_number=f"C{i+2:03d}",
            lot_number=f"L{i+2:03d}",
            description=f"Test Chemical {i+2}",
            manufacturer="Test Manufacturer",
            quantity=50.0 + (i * 25),
            unit="ml",
            location=f"Chemical Storage {i+1}",
            category="Testing",
            status="available",
            created_by=admin_user.id,
            created_at=datetime.utcnow()
        )
        chemicals.append(chemical)
        db_session.add(chemical)

    # Create some user activities
    activities = []
    for _i, tool in enumerate(tools[:2]):
        activity = UserActivity(
            user_id=regular_user.id,
            activity_type="checkout",
            description=f"Checked out {tool.tool_number}",
            timestamp=datetime.utcnow()
        )
        activities.append(activity)
        db_session.add(activity)

    db_session.commit()

    return {
        "tools": tools,
        "chemicals": chemicals,
        "activities": activities
    }

# Test utilities


class TestUtils:
    """Utility functions for testing"""

    @staticmethod
    def assert_json_response(response, expected_status=200):
        """Assert that response is JSON with expected status"""
        assert response.status_code == expected_status
        assert response.content_type == "application/json"
        return response.get_json()

    @staticmethod
    def assert_error_response(response, expected_status=400):
        """Assert that response is an error with expected status"""
        assert response.status_code == expected_status
        data = response.get_json()
        assert "error" in data
        return data

    @staticmethod
    def create_test_user(db_session, employee_number, name="Test User", is_admin=False):
        """Create a test user"""
        user = User(
            name=name,
            employee_number=employee_number,
            department="Testing",
            is_admin=is_admin,
            is_active=True
        )
        user.set_password("test123")
        db_session.add(user)
        db_session.commit()
        return user

@pytest.fixture
def test_utils():
    """Provide test utilities"""
    return TestUtils

@pytest.fixture
def test_user_2(db_session):
    """Create a second test user"""
    from models import User
    
    user = User(
        name="Test User 2",
        employee_number="EMP002",
        department="Engineering",
        is_admin=False,
        is_active=True
    )
    user.set_password("test456")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_channel(db_session, test_user):
    """Create a test channel"""
    from models_messaging import Channel
    
    channel = Channel(
        name="Test Channel",
        description="Test channel for unit tests",
        channel_type="department",
        department="Engineering",
        created_by=test_user.id
    )
    db_session.add(channel)
    db_session.commit()
    return channel


@pytest.fixture
def test_kit(db_session, test_user):
    """Create a test kit"""
    from models_kits import Kit, AircraftType
    
    # Create aircraft type first
    aircraft_type = AircraftType(
        name="Test Aircraft",
        description="Test aircraft type"
    )
    db_session.add(aircraft_type)
    db_session.flush()
    
    kit = Kit(
        name="Test Kit",
        description="Test kit for unit tests",
        aircraft_type_id=aircraft_type.id,
        created_by=test_user.id,
        status="active"
    )
    db_session.add(kit)
    db_session.commit()
    return kit
