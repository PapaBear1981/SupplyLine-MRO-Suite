"""
Unit tests for Kit Transfer API endpoints

Tests all transfer-related API endpoints including:
- Creating transfers (kit-to-kit, kit-to-warehouse, warehouse-to-kit)
- Listing transfers with filters
- Getting transfer details
- Completing transfers
- Cancelling transfers
- Authentication and authorization
- Validation and error handling
"""

import pytest
import json
from models import User, Warehouse, Tool, InventoryTransaction
from models_kits import AircraftType, Kit, KitBox, KitExpendable, KitTransfer


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
def source_warehouse(db_session, admin_user):
    """Create a source warehouse for tool transfers"""
    import uuid

    warehouse = Warehouse(
        name=f'Source Warehouse {uuid.uuid4().hex[:8]}',
        warehouse_type='satellite',
        is_active=True,
        created_by_id=admin_user.id
    )
    db_session.add(warehouse)
    db_session.commit()
    return warehouse


@pytest.fixture
def dest_warehouse(db_session, admin_user):
    """Create a destination warehouse for tool transfers"""
    import uuid

    warehouse = Warehouse(
        name=f'Destination Warehouse {uuid.uuid4().hex[:8]}',
        warehouse_type='satellite',
        is_active=True,
        created_by_id=admin_user.id
    )
    db_session.add(warehouse)
    db_session.commit()
    return warehouse


@pytest.fixture
def warehouse_tool_serial(db_session, source_warehouse):
    """Create a serial-tracked tool in the source warehouse"""
    import uuid

    tool = Tool(
        tool_number=f'SER-{uuid.uuid4().hex[:8]}',
        serial_number=f'SN-{uuid.uuid4().hex[:8]}',
        lot_number=None,
        description='Serial tracked test tool',
        status='available',
        warehouse_id=source_warehouse.id
    )
    db_session.add(tool)
    db_session.commit()
    return tool


@pytest.fixture
def warehouse_tool_lot(db_session, source_warehouse):
    """Create a lot-tracked tool in the source warehouse"""
    import uuid

    tool = Tool(
        tool_number=f'LOT-{uuid.uuid4().hex[:8]}',
        serial_number='',
        lot_number=f'LOT-{uuid.uuid4().hex[:6]}',
        description='Lot tracked test tool',
        status='available',
        warehouse_id=source_warehouse.id
    )
    db_session.add(tool)
    db_session.commit()
    return tool


@pytest.fixture
def source_kit(db_session, admin_user, aircraft_type):
    """Create a source kit for transfers"""
    import uuid
    kit_name = f'Source Kit {uuid.uuid4().hex[:8]}'
    kit = Kit(
        name=kit_name,
        aircraft_type_id=aircraft_type.id,
        description='Source kit for transfers',
        status='active',
        created_by=admin_user.id
    )
    db_session.add(kit)
    db_session.commit()
    return kit


@pytest.fixture
def dest_kit(db_session, admin_user, aircraft_type):
    """Create a destination kit for transfers"""
    import uuid
    kit_name = f'Dest Kit {uuid.uuid4().hex[:8]}'
    kit = Kit(
        name=kit_name,
        aircraft_type_id=aircraft_type.id,
        description='Destination kit for transfers',
        status='active',
        created_by=admin_user.id
    )
    db_session.add(kit)
    db_session.commit()
    return kit


@pytest.fixture
def source_kit_box(db_session, source_kit):
    """Create a box in the source kit"""
    box = KitBox(
        kit_id=source_kit.id,
        box_number='1',
        box_type='expendable',
        description='Expendable items box'
    )
    db_session.add(box)
    db_session.commit()
    return box


@pytest.fixture
def test_expendable(db_session, source_kit, source_kit_box):
    """Create a test expendable in the source kit"""
    expendable = KitExpendable(
        kit_id=source_kit.id,
        box_id=source_kit_box.id,
        part_number='EXP-001',
        description='Safety Wire',
        quantity=100.0,
        unit='ft',
        minimum_stock_level=10.0,
        status='available'
    )
    db_session.add(expendable)
    db_session.commit()
    return expendable


@pytest.fixture
def materials_user(db_session):
    """Create a Materials department user"""
    import uuid
    emp_number = f'MAT{uuid.uuid4().hex[:6]}'

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
def auth_headers_materials(client, materials_user, jwt_manager):
    """Get auth headers for Materials user"""
    # Generate tokens using jwt_manager (pass User object, not ID)
    access_token, refresh_token = jwt_manager.generate_tokens(materials_user)

    # Set cookies on the client
    client.set_cookie('access_token_cookie', access_token)
    client.set_cookie('refresh_token_cookie', refresh_token)

    # Return empty dict since auth is now cookie-based
    return {}


@pytest.fixture
def pending_transfer(db_session, materials_user, test_expendable, source_kit, dest_kit):
    """Create a pending transfer"""
    transfer = KitTransfer(
        item_type='expendable',
        item_id=test_expendable.id,
        from_location_type='kit',
        from_location_id=source_kit.id,
        to_location_type='kit',
        to_location_id=dest_kit.id,
        quantity=10.0,
        transferred_by=materials_user.id,
        status='pending',
        notes='Test transfer'
    )
    db_session.add(transfer)
    db_session.commit()
    return transfer


class TestCreateTransfer:
    """Test creating transfers"""

    def test_create_transfer_kit_to_kit_materials_user(self, client, auth_headers_materials, test_expendable, source_kit, dest_kit):
        """Test creating kit-to-kit transfer as Materials user"""
        transfer_data = {
            'item_type': 'expendable',
            'item_id': test_expendable.id,
            'from_location_type': 'kit',
            'from_location_id': source_kit.id,
            'to_location_type': 'kit',
            'to_location_id': dest_kit.id,
            'quantity': 20.0,
            'notes': 'Transfer for remote operation'
        }

        response = client.post('/api/transfers',
                             json=transfer_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['item_type'] == 'expendable'
        assert data['item_id'] == test_expendable.id
        assert data['from_location_type'] == 'kit'
        assert data['from_location_id'] == source_kit.id
        assert data['to_location_type'] == 'kit'
        assert data['to_location_id'] == dest_kit.id
        assert data['quantity'] == 20.0
        assert data['status'] == 'pending'
        assert data['notes'] == 'Transfer for remote operation'

    def test_create_transfer_kit_to_warehouse(self, client, auth_headers_materials, test_expendable, source_kit, dest_warehouse):
        """Test creating kit-to-warehouse transfer"""
        transfer_data = {
            'item_type': 'expendable',
            'item_id': test_expendable.id,
            'from_location_type': 'kit',
            'from_location_id': source_kit.id,
            'to_location_type': 'warehouse',
            'to_location_id': dest_warehouse.id,
            'quantity': 15.0,
            'notes': 'Return to warehouse'
        }

        response = client.post('/api/transfers',
                             json=transfer_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['to_location_type'] == 'warehouse'
        assert data['to_location_id'] == dest_warehouse.id

    def test_create_transfer_warehouse_to_kit(self, client, auth_headers_materials, test_expendable, dest_kit, source_warehouse):
        """Test creating warehouse-to-kit transfer"""
        transfer_data = {
            'item_type': 'expendable',
            'item_id': test_expendable.id,
            'from_location_type': 'warehouse',
            'from_location_id': source_warehouse.id,
            'to_location_type': 'kit',
            'to_location_id': dest_kit.id,
            'quantity': 25.0,
            'notes': 'Stock kit from warehouse'
        }

        response = client.post('/api/transfers',
                             json=transfer_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['from_location_type'] == 'warehouse'
        assert data['from_location_id'] == source_warehouse.id

    def test_create_transfer_warehouse_to_warehouse_tool_serial(self, client, auth_headers_materials, source_warehouse, dest_warehouse, warehouse_tool_serial):
        """Transfer a serial-tracked tool between warehouses"""
        initial_count = InventoryTransaction.query.filter_by(
            item_type='tool',
            item_id=warehouse_tool_serial.id
        ).count()

        transfer_data = {
            'item_type': 'tool',
            'item_id': warehouse_tool_serial.id,
            'from_location_type': 'warehouse',
            'from_location_id': source_warehouse.id,
            'to_location_type': 'warehouse',
            'to_location_id': dest_warehouse.id,
            'quantity': 1,
            'notes': 'Move serial tool between warehouses'
        }

        response = client.post('/api/transfers',
                               json=transfer_data,
                               headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['item_type'] == 'tool'
        assert data['quantity'] == 1
        assert data['from_location_type'] == 'warehouse'
        assert data['from_location_id'] == source_warehouse.id
        assert data['to_location_type'] == 'warehouse'
        assert data['to_location_id'] == dest_warehouse.id

        updated_tool = Tool.query.get(warehouse_tool_serial.id)
        assert updated_tool.warehouse_id == dest_warehouse.id

        transactions = InventoryTransaction.query.filter_by(
            item_type='tool',
            item_id=warehouse_tool_serial.id
        ).order_by(InventoryTransaction.id.desc()).all()
        assert len(transactions) == initial_count + 1
        transaction = transactions[0]
        assert transaction.transaction_type == 'transfer'
        assert transaction.location_from == source_warehouse.name
        assert transaction.location_to == dest_warehouse.name
        assert transaction.quantity_change == 0

    def test_create_transfer_warehouse_to_warehouse_tool_lot(self, client, auth_headers_materials, source_warehouse, dest_warehouse, warehouse_tool_lot):
        """Transfer a lot-tracked tool between warehouses"""
        transfer_data = {
            'item_type': 'tool',
            'item_id': warehouse_tool_lot.id,
            'from_location_type': 'warehouse',
            'from_location_id': source_warehouse.id,
            'to_location_type': 'warehouse',
            'to_location_id': dest_warehouse.id,
            'quantity': 1,
            'notes': 'Move lot-tracked tool between warehouses'
        }

        response = client.post('/api/transfers',
                               json=transfer_data,
                               headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data['item_type'] == 'tool'
        assert data['quantity'] == 1

        updated_tool = Tool.query.get(warehouse_tool_lot.id)
        assert updated_tool.warehouse_id == dest_warehouse.id
        assert updated_tool.lot_number == warehouse_tool_lot.lot_number
        assert updated_tool.serial_number == warehouse_tool_lot.serial_number

    def test_create_transfer_warehouse_to_warehouse_invalid_quantity(self, client, auth_headers_materials, source_warehouse, dest_warehouse, warehouse_tool_serial):
        """Warehouse-to-warehouse tool transfer must enforce quantity of 1"""
        transfer_data = {
            'item_type': 'tool',
            'item_id': warehouse_tool_serial.id,
            'from_location_type': 'warehouse',
            'from_location_id': source_warehouse.id,
            'to_location_type': 'warehouse',
            'to_location_id': dest_warehouse.id,
            'quantity': 2,
            'notes': 'Invalid quantity for tool transfer'
        }

        response = client.post('/api/transfers',
                               json=transfer_data,
                               headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'quantity of 1' in data['error']

    def test_create_transfer_regular_user_forbidden(self, client, auth_headers_user, test_expendable, source_kit, dest_kit):
        """Test creating transfer as regular user (should fail)"""
        transfer_data = {
            'item_type': 'expendable',
            'item_id': test_expendable.id,
            'from_location_type': 'kit',
            'from_location_id': source_kit.id,
            'to_location_type': 'kit',
            'to_location_id': dest_kit.id,
            'quantity': 10.0
        }

        response = client.post('/api/transfers',
                             json=transfer_data,
                             headers=auth_headers_user)

        assert response.status_code == 403

    def test_create_transfer_missing_required_fields(self, client, auth_headers_materials):
        """Test creating transfer with missing required fields"""
        transfer_data = {
            'item_type': 'expendable',
            'quantity': 10.0
        }

        response = client.post('/api/transfers',
                             json=transfer_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_create_transfer_invalid_location_type(self, client, auth_headers_materials, test_expendable, source_kit):
        """Test creating transfer with invalid location type"""
        transfer_data = {
            'item_type': 'expendable',
            'item_id': test_expendable.id,
            'from_location_type': 'invalid',
            'from_location_id': source_kit.id,
            'to_location_type': 'kit',
            'to_location_id': 1,
            'quantity': 10.0
        }

        response = client.post('/api/transfers',
                             json=transfer_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid from_location_type' in data['error']

    def test_create_transfer_insufficient_quantity(self, client, auth_headers_materials, test_expendable, source_kit, dest_kit):
        """Test creating transfer with insufficient quantity"""
        transfer_data = {
            'item_type': 'expendable',
            'item_id': test_expendable.id,
            'from_location_type': 'kit',
            'from_location_id': source_kit.id,
            'to_location_type': 'kit',
            'to_location_id': dest_kit.id,
            'quantity': 200.0  # More than available (100)
        }

        response = client.post('/api/transfers',
                             json=transfer_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Insufficient quantity' in data['error']

    def test_create_transfer_unauthenticated(self, client, test_expendable, source_kit, dest_kit):
        """Test creating transfer without authentication"""
        transfer_data = {
            'item_type': 'expendable',
            'item_id': test_expendable.id,
            'from_location_type': 'kit',
            'from_location_id': source_kit.id,
            'to_location_type': 'kit',
            'to_location_id': dest_kit.id,
            'quantity': 10.0
        }

        response = client.post('/api/transfers', json=transfer_data)

        assert response.status_code == 401


class TestGetTransfers:
    """Test listing transfers"""

    def test_get_all_transfers(self, client, auth_headers_user, pending_transfer):
        """Test getting all transfers"""
        response = client.get('/api/transfers', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_transfers_filter_by_status(self, client, auth_headers_user, pending_transfer):
        """Test filtering transfers by status"""
        response = client.get('/api/transfers?status=pending', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        for transfer in data:
            assert transfer['status'] == 'pending'

    def test_get_transfers_filter_by_from_kit(self, client, auth_headers_user, pending_transfer, source_kit):
        """Test filtering transfers by source kit"""
        response = client.get(f'/api/transfers?from_kit_id={source_kit.id}', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        for transfer in data:
            assert transfer['from_location_type'] == 'kit'
            assert transfer['from_location_id'] == source_kit.id

    def test_get_transfers_filter_by_to_kit(self, client, auth_headers_user, pending_transfer, dest_kit):
        """Test filtering transfers by destination kit"""
        response = client.get(f'/api/transfers?to_kit_id={dest_kit.id}', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        for transfer in data:
            assert transfer['to_location_type'] == 'kit'
            assert transfer['to_location_id'] == dest_kit.id

    def test_get_transfers_unauthenticated(self, client):
        """Test getting transfers without authentication"""
        response = client.get('/api/transfers')

        assert response.status_code == 401


class TestGetTransferById:
    """Test getting transfer details"""

    def test_get_transfer_by_id(self, client, auth_headers_user, pending_transfer):
        """Test getting specific transfer by ID"""
        response = client.get(f'/api/transfers/{pending_transfer.id}', headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['id'] == pending_transfer.id
        assert data['status'] == 'pending'
        assert 'item_type' in data
        assert 'quantity' in data

    def test_get_transfer_not_found(self, client, auth_headers_user):
        """Test getting non-existent transfer"""
        response = client.get('/api/transfers/99999', headers=auth_headers_user)

        assert response.status_code == 404

    def test_get_transfer_unauthenticated(self, client, pending_transfer):
        """Test getting transfer without authentication"""
        response = client.get(f'/api/transfers/{pending_transfer.id}')

        assert response.status_code == 401


class TestCompleteTransfer:
    """Test completing transfers"""

    def test_complete_transfer_materials_user(self, client, auth_headers_materials, pending_transfer, test_expendable):
        """Test completing transfer as Materials user"""
        original_quantity = test_expendable.quantity

        response = client.put(f'/api/transfers/{pending_transfer.id}/complete',
                            headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['status'] == 'completed'
        assert data['completed_date'] is not None

        # Verify source item quantity was reduced
        from models_kits import KitExpendable
        updated_item = KitExpendable.query.get(test_expendable.id)
        assert updated_item.quantity == original_quantity - pending_transfer.quantity

    def test_complete_transfer_regular_user_forbidden(self, client, auth_headers_user, pending_transfer):
        """Test completing transfer as regular user (should fail)"""
        response = client.put(f'/api/transfers/{pending_transfer.id}/complete',
                            headers=auth_headers_user)

        assert response.status_code == 403

    def test_complete_transfer_not_pending(self, client, auth_headers_materials, db_session, materials_user, test_expendable, source_kit, dest_kit):
        """Test completing transfer that is not in pending status"""
        # Create a completed transfer
        transfer = KitTransfer(
            item_type='expendable',
            item_id=test_expendable.id,
            from_location_type='kit',
            from_location_id=source_kit.id,
            to_location_type='kit',
            to_location_id=dest_kit.id,
            quantity=5.0,
            transferred_by=materials_user.id,
            status='completed'
        )
        db_session.add(transfer)
        db_session.commit()

        response = client.put(f'/api/transfers/{transfer.id}/complete',
                            headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'not in pending status' in data['error']

    def test_complete_transfer_not_found(self, client, auth_headers_materials):
        """Test completing non-existent transfer"""
        response = client.put('/api/transfers/99999/complete',
                            headers=auth_headers_materials)

        assert response.status_code == 404

    def test_complete_transfer_unauthenticated(self, client, pending_transfer):
        """Test completing transfer without authentication"""
        response = client.put(f'/api/transfers/{pending_transfer.id}/complete')

        assert response.status_code == 401


class TestCancelTransfer:
    """Test cancelling transfers"""

    def test_cancel_transfer_materials_user(self, client, auth_headers_materials, pending_transfer):
        """Test cancelling transfer as Materials user"""
        response = client.put(f'/api/transfers/{pending_transfer.id}/cancel',
                            headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['status'] == 'cancelled'

        # Verify transfer is cancelled in database
        from models_kits import KitTransfer
        updated_transfer = KitTransfer.query.get(pending_transfer.id)
        assert updated_transfer.status == 'cancelled'

    def test_cancel_transfer_regular_user_forbidden(self, client, auth_headers_user, pending_transfer):
        """Test cancelling transfer as regular user (should fail)"""
        response = client.put(f'/api/transfers/{pending_transfer.id}/cancel',
                            headers=auth_headers_user)

        assert response.status_code == 403

    def test_cancel_transfer_not_pending(self, client, auth_headers_materials, db_session, materials_user, test_expendable, source_kit, dest_kit):
        """Test cancelling transfer that is not in pending status"""
        # Create a completed transfer
        transfer = KitTransfer(
            item_type='expendable',
            item_id=test_expendable.id,
            from_location_type='kit',
            from_location_id=source_kit.id,
            to_location_type='kit',
            to_location_id=dest_kit.id,
            quantity=5.0,
            transferred_by=materials_user.id,
            status='completed'
        )
        db_session.add(transfer)
        db_session.commit()

        response = client.put(f'/api/transfers/{transfer.id}/cancel',
                            headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Can only cancel pending transfers' in data['error']

    def test_cancel_transfer_not_found(self, client, auth_headers_materials):
        """Test cancelling non-existent transfer"""
        response = client.put('/api/transfers/99999/cancel',
                            headers=auth_headers_materials)

        assert response.status_code == 404

    def test_cancel_transfer_unauthenticated(self, client, pending_transfer):
        """Test cancelling transfer without authentication"""
        response = client.put(f'/api/transfers/{pending_transfer.id}/cancel')

        assert response.status_code == 401
