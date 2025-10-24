"""
Pytest configuration and fixtures for SupplyLine MRO Suite backend tests
"""

import os
import sys
import tempfile

import pytest
from werkzeug.security import generate_password_hash

# Ensure the backend directory is on the Python path so absolute imports work
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# These globals are populated lazily after we configure the environment for tests
create_app = None
JWTManager = None
db = None
User = None
Tool = None
Chemical = None
Role = None
Permission = None
UserRole = None
RolePermission = None


def _ensure_imports():
    """Lazy-load application modules when first needed."""
    global create_app, JWTManager, db, User, Tool, Chemical, Role, Permission, UserRole, RolePermission

    if create_app is None:
        from app import create_app as _create_app
        from auth import JWTManager as _JWTManager
        from models import (
            Permission as _Permission,
            Role as _Role,
            RolePermission as _RolePermission,
            Tool as _Tool,
            User as _User,
            UserRole as _UserRole,
            Chemical as _Chemical,
            db as _db,
        )

        create_app = _create_app
        JWTManager = _JWTManager
        db = _db
        User = _User
        Tool = _Tool
        Chemical = _Chemical
        Role = _Role
        Permission = _Permission
        UserRole = _UserRole
        RolePermission = _RolePermission


@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    # Create a temporary database file
    # B108 Mitigation: Use mkstemp for secure temporary file creation (avoids mktemp race condition).
    # File descriptor (db_fd) is closed and file (db_path) is unlinked in the 'finally' block.
    db_fd, db_path = tempfile.mkstemp()

    # Configure environment for testing before app creation so Config picks it up
    original_db_url = os.environ.get('DATABASE_URL')
    original_flask_env = os.environ.get('FLASK_ENV')
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
    os.environ['FLASK_ENV'] = 'testing'

    try:
        _ensure_imports()

        app = create_app()
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key',
            'JWT_SECRET_KEY': 'test-jwt-secret-key'
        })

        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    finally:
        # Restore environment configuration
        if original_db_url is not None:
            os.environ['DATABASE_URL'] = original_db_url
        else:
            os.environ.pop('DATABASE_URL', None)

        if original_flask_env is not None:
            os.environ['FLASK_ENV'] = original_flask_env
        else:
            os.environ.pop('FLASK_ENV', None)

        # Dispose of the database engine connection to release the file handle on Windows
        db.engine.dispose()

        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Create database session for testing"""
    _ensure_imports()
    with app.app_context():
        # Clear all tables
        db.session.query(UserRole).delete()
        db.session.query(RolePermission).delete()
        db.session.query(User).delete()
        db.session.query(Tool).delete()
        db.session.query(Chemical).delete()
        db.session.query(Role).delete()
        db.session.query(Permission).delete()
        db.session.commit()
        yield db.session
        db.session.rollback()


@pytest.fixture
def admin_user(db_session):
    """Create admin user for testing"""
    _ensure_imports()
    user = User(
        name='Test Admin',
        employee_number='ADMIN001',
        department='IT',
        password_hash=generate_password_hash('admin123'),
        is_admin=True,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def regular_user(db_session):
    """Create regular user for testing"""
    _ensure_imports()
    user = User(
        name='Test User',
        employee_number='USER001',
        department='Engineering',
        password_hash=generate_password_hash('user123'),
        is_admin=False,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def materials_user(db_session):
    """Create materials department user for testing"""
    _ensure_imports()
    user = User(
        name='Materials User',
        employee_number='MAT001',
        department='Materials',
        password_hash=generate_password_hash('materials123'),
        is_admin=False,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_tool(db_session):
    """Create test tool"""
    _ensure_imports()
    tool = Tool(
        tool_number='T001',
        serial_number='S001',
        description='Test Tool',
        condition='Good',
        location='Test Location',
        category='Testing',
        status='available'
    )
    db_session.add(tool)
    db_session.commit()
    return tool


@pytest.fixture
def test_chemical(db_session):
    """Create test chemical"""
    _ensure_imports()
    chemical = Chemical(
        part_number='C001',
        lot_number='L001',
        description='Test Chemical',
        manufacturer='Test Manufacturer',
        quantity=100.0,
        unit='ml',
        location='Test Location',
        category='Testing',
        status='available'
    )
    db_session.add(chemical)
    db_session.commit()
    return chemical


@pytest.fixture
def admin_token(app, admin_user):
    """Generate JWT token for admin user"""
    _ensure_imports()
    with app.app_context():
        tokens = JWTManager.generate_tokens(admin_user)
        return tokens['access_token']


@pytest.fixture
def user_token(app, regular_user):
    """Generate JWT token for regular user"""
    _ensure_imports()
    with app.app_context():
        tokens = JWTManager.generate_tokens(regular_user)
        return tokens['access_token']


@pytest.fixture
def materials_token(app, materials_user):
    """Generate JWT token for materials user"""
    _ensure_imports()
    with app.app_context():
        tokens = JWTManager.generate_tokens(materials_user)
        return tokens['access_token']


@pytest.fixture
def auth_headers_admin(admin_token):
    """Create authorization headers for admin user"""
    return {'Authorization': f'Bearer {admin_token}'}


@pytest.fixture
def auth_headers_user(user_token):
    """Create authorization headers for regular user"""
    return {'Authorization': f'Bearer {user_token}'}


@pytest.fixture
def auth_headers_materials(materials_token):
    """Create authorization headers for materials user"""
    return {'Authorization': f'Bearer {materials_token}'}


@pytest.fixture
def sample_roles_permissions(db_session):
    """Create sample roles and permissions for testing"""
    # Create permissions
    permissions = [
        Permission(name='view_tools', description='View tools'),
        Permission(name='manage_tools', description='Manage tools'),
        Permission(name='view_chemicals', description='View chemicals'),
        Permission(name='manage_chemicals', description='Manage chemicals'),
    ]

    for perm in permissions:
        db_session.add(perm)

    # Create roles
    admin_role = Role(name='admin', description='Administrator')
    user_role = Role(name='user', description='Regular User')

    db_session.add(admin_role)
    db_session.add(user_role)
    db_session.flush()

    # Assign permissions to roles
    for perm in permissions:
        role_perm = RolePermission(role_id=admin_role.id, permission_id=perm.id)
        db_session.add(role_perm)

    # Give user role basic permissions
    view_tools_perm = next(p for p in permissions if p.name == 'view_tools')
    user_role_perm = RolePermission(role_id=user_role.id, permission_id=view_tools_perm.id)
    db_session.add(user_role_perm)

    db_session.commit()

    return {
        'admin_role': admin_role,
        'user_role': user_role,
        'permissions': permissions
    }
