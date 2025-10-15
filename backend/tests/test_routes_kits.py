"""
Unit tests for Kit API endpoints

Tests all kit-related API endpoints including:
- Aircraft type management
- Kit CRUD operations
- Kit wizard
- Box management
- Item management
- Expendable management
- Issuance operations
- Analytics and alerts
"""

import pytest
import json
from models import User
from models_kits import AircraftType, Kit, KitBox, KitExpendable, KitIssuance


@pytest.fixture
def aircraft_type(db_session):
    """Create a test aircraft type"""
    aircraft_type = AircraftType.query.filter_by(name='Q400').first()
    if not aircraft_type:
        aircraft_type = AircraftType(name='Q400', description='Test Aircraft', is_active=True)
        db_session.add(aircraft_type)
        db_session.commit()
    return aircraft_type


@pytest.fixture
def test_kit(db_session, admin_user, aircraft_type):
    """Create a test kit with unique name"""
    import uuid
    kit_name = f'Test Kit {uuid.uuid4().hex[:8]}'
    kit = Kit(
        name=kit_name,
        aircraft_type_id=aircraft_type.id,
        description='Test kit for unit tests',
        status='active',
        created_by=admin_user.id
    )
    db_session.add(kit)
    db_session.commit()
    return kit


@pytest.fixture
def test_kit_box(db_session, test_kit):
    """Create a test kit box"""
    box = KitBox(
        kit_id=test_kit.id,
        box_number='1',
        box_type='expendable',
        description='Expendable items box'
    )
    db_session.add(box)
    db_session.commit()
    return box


@pytest.fixture
def materials_user(db_session):
    """Create a Materials department user with unique employee number"""
    import uuid
    emp_number = f'MAT{uuid.uuid4().hex[:6]}'

    # Check if user already exists
    existing_user = User.query.filter_by(employee_number=emp_number).first()
    if existing_user:
        return existing_user

    user = User(
        name='Materials User',
        employee_number=emp_number,
        department='Materials',
        is_admin=False,
        is_active=True
    )
    user.set_password('materials123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def auth_headers_materials(client, materials_user):
    """Get auth headers for Materials user"""
    response = client.post('/api/auth/login', json={
        'employee_number': materials_user.employee_number,
        'password': 'materials123'
    })
    data = json.loads(response.data)
    return {'Authorization': f'Bearer {data["access_token"]}'}


class TestAircraftTypeEndpoints:
    """Test aircraft type management endpoints"""

    def test_get_aircraft_types_authenticated(self, client, auth_headers_user, aircraft_type):
        """Test getting aircraft types list with authentication"""
        response = client.get('/api/aircraft-types', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(at['name'] == 'Q400' for at in data)

    def test_get_aircraft_types_unauthenticated(self, client):
        """Test getting aircraft types without authentication"""
        response = client.get('/api/aircraft-types')

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Authentication required'

    def test_get_aircraft_types_include_inactive(self, client, auth_headers_user, db_session):
        """Test getting aircraft types including inactive ones"""
        # Create inactive aircraft type
        inactive_type = AircraftType(name='Inactive Type', is_active=False)
        db_session.add(inactive_type)
        db_session.commit()

        # Without include_inactive
        response = client.get('/api/aircraft-types', headers=auth_headers_user)
        data = json.loads(response.data)
        assert not any(at['name'] == 'Inactive Type' for at in data)

        # With include_inactive
        response = client.get('/api/aircraft-types?include_inactive=true', headers=auth_headers_user)
        data = json.loads(response.data)
        assert any(at['name'] == 'Inactive Type' for at in data)

    def test_create_aircraft_type_admin(self, client, auth_headers_admin, db_session):
        """Test creating aircraft type as admin"""
        aircraft_data = {
            'name': 'Boeing 737',
            'description': 'Boeing 737 aircraft'
        }

        response = client.post('/api/aircraft-types',
                             json=aircraft_data,
                             headers=auth_headers_admin)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['name'] == 'Boeing 737'
        assert data['description'] == 'Boeing 737 aircraft'
        assert data['is_active'] is True

        # Verify created in database
        aircraft_type = AircraftType.query.filter_by(name='Boeing 737').first()
        assert aircraft_type is not None

    def test_create_aircraft_type_regular_user(self, client, auth_headers_user):
        """Test creating aircraft type as regular user (should fail)"""
        aircraft_data = {
            'name': 'Unauthorized Aircraft',
            'description': 'Should not be created'
        }

        response = client.post('/api/aircraft-types',
                             json=aircraft_data,
                             headers=auth_headers_user)

        assert response.status_code == 403

    def test_create_aircraft_type_duplicate(self, client, auth_headers_admin, aircraft_type):
        """Test creating duplicate aircraft type (should fail)"""
        aircraft_data = {
            'name': 'Q400',
            'description': 'Duplicate'
        }

        response = client.post('/api/aircraft-types',
                             json=aircraft_data,
                             headers=auth_headers_admin)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already exists' in data['error']

    def test_create_aircraft_type_missing_name(self, client, auth_headers_admin):
        """Test creating aircraft type without name (should fail)"""
        aircraft_data = {
            'description': 'No name provided'
        }

        response = client.post('/api/aircraft-types',
                             json=aircraft_data,
                             headers=auth_headers_admin)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'required' in data['error'].lower()

    def test_update_aircraft_type_admin(self, client, auth_headers_admin, aircraft_type):
        """Test updating aircraft type as admin"""
        update_data = {
            'description': 'Updated description',
            'is_active': False
        }

        response = client.put(f'/api/aircraft-types/{aircraft_type.id}',
                            json=update_data,
                            headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['description'] == 'Updated description'
        assert data['is_active'] is False

    def test_update_aircraft_type_regular_user(self, client, auth_headers_user, aircraft_type):
        """Test updating aircraft type as regular user (should fail)"""
        update_data = {
            'description': 'Unauthorized update'
        }

        response = client.put(f'/api/aircraft-types/{aircraft_type.id}',
                            json=update_data,
                            headers=auth_headers_user)

        assert response.status_code == 403

    def test_deactivate_aircraft_type_admin(self, client, auth_headers_admin, aircraft_type):
        """Test deactivating aircraft type as admin"""
        response = client.delete(f'/api/aircraft-types/{aircraft_type.id}',
                               headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['is_active'] is False
        assert 'deactivated' in data['message'].lower()

    def test_deactivate_aircraft_type_regular_user(self, client, auth_headers_user, aircraft_type):
        """Test deactivating aircraft type as regular user (should fail)"""
        response = client.delete(f'/api/aircraft-types/{aircraft_type.id}',
                               headers=auth_headers_user)

        assert response.status_code == 403


class TestKitCRUDEndpoints:
    """Test kit CRUD operation endpoints"""

    def test_get_kits_authenticated(self, client, auth_headers_user, test_kit):
        """Test getting kits list with authentication"""
        response = client.get('/api/kits', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_kits_unauthenticated(self, client):
        """Test getting kits without authentication"""
        response = client.get('/api/kits')

        assert response.status_code == 401

    def test_get_kit_by_id(self, client, auth_headers_user, test_kit):
        """Test getting specific kit by ID"""
        response = client.get(f'/api/kits/{test_kit.id}', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['id'] == test_kit.id
        assert 'name' in data
        assert data['status'] == 'active'

    def test_get_kit_not_found(self, client, auth_headers_user):
        """Test getting non-existent kit"""
        response = client.get('/api/kits/99999', headers=auth_headers_user)

        assert response.status_code == 404


    def test_create_kit_materials_user(self, client, auth_headers_materials, aircraft_type, db_session):
        """Test creating kit as Materials user"""
        kit_data = {
            'name': 'New Test Kit',
            'aircraft_type_id': aircraft_type.id,
            'description': 'Created by Materials user',
            'status': 'active'
        }

        response = client.post('/api/kits',
                             json=kit_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['name'] == 'New Test Kit'
        assert data['aircraft_type_id'] == aircraft_type.id

        # Verify created in database
        kit = Kit.query.filter_by(name='New Test Kit').first()
        assert kit is not None

    def test_create_kit_regular_user(self, client, auth_headers_user, aircraft_type):
        """Test creating kit as regular user (should fail)"""
        kit_data = {
            'name': 'Unauthorized Kit',
            'aircraft_type_id': aircraft_type.id
        }

        response = client.post('/api/kits',
                             json=kit_data,
                             headers=auth_headers_user)

        assert response.status_code == 403

    def test_create_kit_missing_required_fields(self, client, auth_headers_materials):
        """Test creating kit without required fields"""
        kit_data = {
            'description': 'Missing name and aircraft type'
        }

        response = client.post('/api/kits',
                             json=kit_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_update_kit_materials_user(self, client, auth_headers_materials, test_kit):
        """Test updating kit as Materials user"""
        update_data = {
            'description': 'Updated description',
            'status': 'maintenance'
        }

        response = client.put(f'/api/kits/{test_kit.id}',
                            json=update_data,
                            headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['description'] == 'Updated description'
        assert data['status'] == 'maintenance'

    def test_update_kit_regular_user(self, client, auth_headers_user, test_kit):
        """Test updating kit as regular user (should fail)"""
        update_data = {
            'description': 'Unauthorized update'
        }

        response = client.put(f'/api/kits/{test_kit.id}',
                            json=update_data,
                            headers=auth_headers_user)

        assert response.status_code == 403

    def test_delete_kit_materials_user(self, client, auth_headers_materials, test_kit):
        """Test deleting kit as Materials user"""
        response = client.delete(f'/api/kits/{test_kit.id}',
                               headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'deleted' in data['message'].lower()

        # Verify kit is soft deleted (status set to inactive)
        kit = Kit.query.get(test_kit.id)
        assert kit is not None
        assert kit.status == 'inactive'

    def test_delete_kit_regular_user(self, client, auth_headers_user, test_kit):
        """Test deleting kit as regular user (should fail)"""
        response = client.delete(f'/api/kits/{test_kit.id}',
                               headers=auth_headers_user)

        assert response.status_code == 403

    def test_duplicate_kit_materials_user(self, client, auth_headers_materials, test_kit, db_session):
        """Test duplicating kit as Materials user"""
        duplicate_data = {
            'name': 'Duplicated Kit'
        }

        response = client.post(f'/api/kits/{test_kit.id}/duplicate',
                             json=duplicate_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['name'] == 'Duplicated Kit'
        assert data['aircraft_type_id'] == test_kit.aircraft_type_id

        # Verify duplicated kit exists
        duplicated_kit = Kit.query.filter_by(name='Duplicated Kit').first()
        assert duplicated_kit is not None


class TestKitWizardEndpoint:
    """Test kit wizard endpoint"""

    def test_kit_wizard_step1_aircraft_selection(self, client, auth_headers_materials, aircraft_type):
        """Test kit wizard step 1 - aircraft type selection"""
        wizard_data = {
            'step': 1,
            'aircraft_type_id': aircraft_type.id
        }

        response = client.post('/api/kits/wizard',
                             json=wizard_data,
                             headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['step'] == 1
        assert 'aircraft_types' in data
        assert isinstance(data['aircraft_types'], list)

    def test_kit_wizard_step2_kit_details(self, client, auth_headers_materials, aircraft_type):
        """Test kit wizard step 2 - kit details"""
        wizard_data = {
            'step': 2,
            'aircraft_type_id': aircraft_type.id,
            'name': 'Wizard Created Kit',
            'description': 'Created via wizard'
        }

        response = client.post('/api/kits/wizard',
                             json=wizard_data,
                             headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['step'] == 2
        assert data['valid'] is True


class TestKitBoxEndpoints:
    """Test kit box management endpoints"""

    def test_get_kit_boxes(self, client, auth_headers_user, test_kit, test_kit_box):
        """Test getting kit boxes"""
        response = client.get(f'/api/kits/{test_kit.id}/boxes', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]['box_type'] == 'expendable'

    def test_add_kit_box_materials_user(self, client, auth_headers_materials, test_kit, db_session):
        """Test adding box to kit as Materials user"""
        box_data = {
            'box_number': '2',
            'box_type': 'tooling',
            'description': 'Tooling box'
        }

        response = client.post(f'/api/kits/{test_kit.id}/boxes',
                             json=box_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['box_number'] == '2'
        assert data['box_type'] == 'tooling'

    def test_add_kit_box_regular_user(self, client, auth_headers_user, test_kit):
        """Test adding box as regular user (should fail)"""
        box_data = {
            'box_number': '3',
            'box_type': 'consumable'
        }

        response = client.post(f'/api/kits/{test_kit.id}/boxes',
                             json=box_data,
                             headers=auth_headers_user)

        assert response.status_code == 403

    def test_update_kit_box(self, client, auth_headers_materials, test_kit, test_kit_box):
        """Test updating kit box"""
        update_data = {
            'description': 'Updated box description'
        }

        response = client.put(f'/api/kits/{test_kit.id}/boxes/{test_kit_box.id}',
                            json=update_data,
                            headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['description'] == 'Updated box description'

    def test_delete_kit_box(self, client, auth_headers_materials, test_kit, test_kit_box):
        """Test deleting kit box"""
        response = client.delete(f'/api/kits/{test_kit.id}/boxes/{test_kit_box.id}',
                               headers=auth_headers_materials)

        assert response.status_code == 200

        # Verify box is deleted
        box = KitBox.query.get(test_kit_box.id)
        assert box is None


class TestKitItemEndpoints:
    """Test kit item management endpoints"""

    def test_get_kit_items(self, client, auth_headers_user, test_kit):
        """Test getting kit items"""
        response = client.get(f'/api/kits/{test_kit.id}/items', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, dict)
        assert 'items' in data
        assert 'expendables' in data

    def test_get_kit_items_with_filters(self, client, auth_headers_user, test_kit):
        """Test getting kit items with filters"""
        response = client.get(f'/api/kits/{test_kit.id}/items?item_type=tool&status=available',
                            headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, dict)
        assert 'items' in data
        assert 'expendables' in data

    def test_add_kit_item_materials_user(self, client, auth_headers_materials, test_kit, test_kit_box, test_tool, db_session):
        """Test adding item to kit as Materials user"""
        item_data = {
            'box_id': test_kit_box.id,
            'item_type': 'tool',
            'item_id': test_tool.id,
            'quantity': 1,
            'location': 'Box 1',
            'status': 'available'
        }

        response = client.post(f'/api/kits/{test_kit.id}/items',
                             json=item_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['item_type'] == 'tool'
        assert data['quantity'] == 1

    def test_add_kit_item_regular_user(self, client, auth_headers_user, test_kit, test_kit_box, test_tool):
        """Test adding item as regular user (should fail)"""
        item_data = {
            'box_id': test_kit_box.id,
            'item_type': 'tool',
            'item_id': test_tool.id
        }

        response = client.post(f'/api/kits/{test_kit.id}/items',
                             json=item_data,
                             headers=auth_headers_user)

        assert response.status_code == 403


class TestKitExpendableEndpoints:
    """Test kit expendable management endpoints"""

    def test_get_kit_expendables(self, client, auth_headers_user, test_kit):
        """Test getting kit expendables"""
        response = client.get(f'/api/kits/{test_kit.id}/expendables', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)

    def test_add_kit_expendable_materials_user(self, client, auth_headers_materials, test_kit, test_kit_box, db_session):
        """Test adding expendable to kit as Materials user"""
        expendable_data = {
            'box_id': test_kit_box.id,
            'part_number': 'EXP-001',
            'description': 'Safety Wire',
            'quantity': 100,
            'unit': 'ft',
            'location': 'Box 1',
            'status': 'available'
        }

        response = client.post(f'/api/kits/{test_kit.id}/expendables',
                             json=expendable_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['part_number'] == 'EXP-001'
        assert data['quantity'] == 100


class TestKitIssuanceEndpoints:
    """Test kit issuance endpoints"""

    def test_issue_from_kit(self, client, auth_headers_user, test_kit, test_kit_box, db_session):
        """Test issuing items from kit"""
        # First add an expendable to issue
        expendable = KitExpendable(
            kit_id=test_kit.id,
            box_id=test_kit_box.id,
            part_number='EXP-TEST',
            description='Test Expendable',
            quantity=50,
            unit='ea',
            status='available'
        )
        db_session.add(expendable)
        db_session.commit()

        issuance_data = {
            'item_type': 'expendable',
            'item_id': expendable.id,
            'quantity': 10,
            'purpose': 'Maintenance',
            'work_order': 'WO-12345'
        }

        response = client.post(f'/api/kits/{test_kit.id}/issue',
                             json=issuance_data,
                             headers=auth_headers_user)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['quantity'] == 10
        assert data['purpose'] == 'Maintenance'

        # Verify expendable quantity was reduced
        db_session.refresh(expendable)
        assert expendable.quantity == 40

    def test_issue_from_kit_insufficient_quantity(self, client, auth_headers_user, test_kit, test_kit_box, db_session):
        """Test issuing more than available quantity (should fail)"""
        expendable = KitExpendable(
            kit_id=test_kit.id,
            box_id=test_kit_box.id,
            part_number='EXP-LOW',
            description='Low Stock Item',
            quantity=5,
            unit='ea',
            status='available'
        )
        db_session.add(expendable)
        db_session.commit()

        issuance_data = {
            'item_type': 'expendable',
            'item_id': expendable.id,
            'quantity': 10,
            'purpose': 'Maintenance'
        }

        response = client.post(f'/api/kits/{test_kit.id}/issue',
                             json=issuance_data,
                             headers=auth_headers_user)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'insufficient' in data['error'].lower() or 'not enough' in data['error'].lower()

    def test_get_kit_issuances(self, client, auth_headers_user, test_kit):
        """Test getting kit issuance history"""
        response = client.get(f'/api/kits/{test_kit.id}/issuances', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)

    def test_get_kit_issuance_by_id(self, client, auth_headers_user, test_kit, db_session, admin_user):
        """Test getting specific issuance by ID"""
        # Create an issuance
        issuance = KitIssuance(
            kit_id=test_kit.id,
            item_type='expendable',
            item_id=1,
            issued_by=admin_user.id,
            quantity=5,
            purpose='Test'
        )
        db_session.add(issuance)
        db_session.commit()

        response = client.get(f'/api/kits/{test_kit.id}/issuances/{issuance.id}',
                            headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['id'] == issuance.id
        assert data['quantity'] == 5


class TestKitAnalyticsEndpoints:
    """Test kit analytics and reporting endpoints"""

    def test_get_kit_analytics(self, client, auth_headers_user, test_kit):
        """Test getting kit analytics"""
        response = client.get(f'/api/kits/{test_kit.id}/analytics', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'inventory' in data
        assert 'total_items' in data['inventory']
        assert 'issuances' in data

    def test_get_inventory_report(self, client, auth_headers_user):
        """Test getting inventory report"""
        response = client.get('/api/kits/reports/inventory', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list) or isinstance(data, dict)

    def test_get_inventory_report_with_filters(self, client, auth_headers_user, aircraft_type):
        """Test getting inventory report with filters"""
        response = client.get(f'/api/kits/reports/inventory?aircraft_type_id={aircraft_type.id}',
                            headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list) or isinstance(data, dict)


class TestKitAlertsEndpoints:
    """Test kit alerts endpoints"""

    def test_get_kit_alerts(self, client, auth_headers_user, test_kit):
        """Test getting kit alerts"""
        response = client.get(f'/api/kits/{test_kit.id}/alerts', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, dict)
        assert 'alerts' in data
        assert isinstance(data['alerts'], list)
        # Alerts should include low stock, expiring items, etc.

    def test_get_kit_alerts_unauthenticated(self, client, test_kit):
        """Test getting kit alerts without authentication"""
        response = client.get(f'/api/kits/{test_kit.id}/alerts')

        assert response.status_code == 401
