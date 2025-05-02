import pytest
from backend.app import create_app
from backend.models import db, Tool, User, Checkout, AuditLog
import json
from datetime import datetime

@pytest.fixture(scope='module')
def test_app():
    app = create_app()
    app.config.from_object('backend.config.TestingConfig')
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

def test_create_tool(test_client, init_database):
    tool_data = {
        'tool_number': 'T001',
        'serial_number': 'SN001',
        'description': 'Hammer',
        'condition': 'New',
        'location': 'Warehouse'
    }
    response = test_client.post('/tools', json=tool_data)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data

    # Verify tool created in database
    with test_client.application.app_context():
        tool = Tool.query.filter_by(id=data['id']).first()
        assert tool is not None
        assert tool.tool_number == 'T001'

def test_get_tools(test_client, init_database):
    tool1 = Tool(tool_number='T001', serial_number='SN001', description='Hammer', condition='New', location='Warehouse')
    tool2 = Tool(tool_number='T002', serial_number='SN002', description='Drill', condition='Used', location='Shelf')
    with test_client.application.app_context():
        db.session.add_all([tool1, tool2])
        db.session.commit()

    response = test_client.get('/tools')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]['tool_number'] == 'T001'
    assert data[1]['tool_number'] == 'T002'

def test_create_user(test_client, init_database):
    user_data = {
        'name': 'John Doe',
        'employee_number': 'E123',
        'department': 'Engineering',
        'password_hash': 'hashed_password' # In a real app, this would be hashed
    }
    response = test_client.post('/users', json=user_data)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data

    # Verify user created in database
    with test_client.application.app_context():
        user = User.query.filter_by(id=data['id']).first()
        assert user is not None
        assert user.employee_number == 'E123'

def test_get_users(test_client, init_database):
    user1 = User(name='John Doe', employee_number='E123', department='Engineering', password_hash='hash1')
    user2 = User(name='Jane Smith', employee_number='E456', department='Marketing', password_hash='hash2')
    with test_client.application.app_context():
        db.session.add_all([user1, user2])
        db.session.commit()

    response = test_client.get('/users')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]['employee_number'] == 'E123'
    assert data[1]['employee_number'] == 'E456'

def test_create_checkout(test_client, init_database):
    tool = Tool(tool_number='T001', serial_number='SN001', description='Hammer', condition='New', location='Warehouse')
    user = User(name='John Doe', employee_number='E123', department='Engineering', password_hash='hash')
    with test_client.application.app_context():
        db.session.add_all([tool, user])
        db.session.commit()
        tool_id = tool.id
        user_id = user.id

    checkout_data = {
        'tool_id': tool_id,
        'user_id': user_id
    }
    response = test_client.post('/checkouts', json=checkout_data)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data

    # Verify checkout created in database
    with test_client.application.app_context():
        checkout = Checkout.query.filter_by(id=data['id']).first()
        assert checkout is not None
        assert checkout.tool_id == tool_id
        assert checkout.user_id == user_id

def test_get_checkouts(test_client, init_database):
    tool = Tool(tool_number='T001', serial_number='SN001', description='Hammer', condition='New', location='Warehouse')
    user = User(name='John Doe', employee_number='E123', department='Engineering', password_hash='hash')
    with test_client.application.app_context():
        db.session.add_all([tool, user])
        db.session.commit()
        tool_id = tool.id
        user_id = user.id
        checkout1 = Checkout(tool_id=tool_id, user_id=user_id)
        checkout2 = Checkout(tool_id=tool_id, user_id=user_id)
        db.session.add_all([checkout1, checkout2])
        db.session.commit()

    response = test_client.get('/checkouts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]['tool_id'] == tool_id
    assert data[1]['user_id'] == user_id

def test_return_checkout(test_client, init_database):
    tool = Tool(tool_number='T001', serial_number='SN001', description='Hammer', condition='New', location='Warehouse')
    user = User(name='John Doe', employee_number='E123', department='Engineering', password_hash='hash')
    with test_client.application.app_context():
        db.session.add_all([tool, user])
        db.session.commit()
        tool_id = tool.id
        user_id = user.id
        checkout = Checkout(tool_id=tool_id, user_id=user_id)
        db.session.add(checkout)
        db.session.commit()
        checkout_id = checkout.id

    response = test_client.post(f'/checkouts/{checkout_id}/return')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'id' in data

    # Verify return_date is set in database
    with test_client.application.app_context():
        checkout = Checkout.query.filter_by(id=checkout_id).first()
        assert checkout.return_date is not None

def test_get_audit_logs(test_client, init_database):
    log1 = AuditLog(action_type='create_tool', action_details='Created tool 1')
    log2 = AuditLog(action_type='create_user', action_details='Created user 1')
    with test_client.application.app_context():
        db.session.add_all([log1, log2])
        db.session.commit()

    response = test_client.get('/audit')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]['action_type'] == 'create_user' # Ordered by timestamp desc
    assert data[1]['action_type'] == 'create_tool'