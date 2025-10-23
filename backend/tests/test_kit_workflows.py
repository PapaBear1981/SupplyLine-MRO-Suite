"""
Integration tests for Kit Workflows

Tests end-to-end workflows that span multiple API endpoints:
- Complete kit creation workflow (wizard + boxes + items)
- Issuance triggering automatic reorder
- Transfer completing and updating inventory
- Message thread creation and replies
- Reorder approval and fulfillment workflow
- Multi-step operations with state changes
"""

import pytest
import json
from models import User
from models_kits import (
    AircraftType, Kit, KitBox, KitExpendable, KitTransfer,
    KitReorderRequest
)


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


class TestCompleteKitCreationWorkflow:
    """Test complete kit creation workflow using wizard"""

    def test_complete_kit_creation_via_wizard(self, client, auth_headers_materials, aircraft_type, db_session):
        """Test creating a complete kit through the wizard workflow"""

        # Step 1: Get aircraft types
        response = client.post('/api/kits/wizard',
                             json={'step': 1},
                             headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['step'] == 1
        assert 'aircraft_types' in data
        assert len(data['aircraft_types']) > 0

        # Step 2: Validate kit details (name and aircraft type)
        import uuid
        kit_name = f'Integration Test Kit {uuid.uuid4().hex[:8]}'

        response = client.post('/api/kits/wizard',
                             json={
                                 'step': 2,
                                 'name': kit_name,
                                 'aircraft_type_id': aircraft_type.id
                             },
                             headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['step'] == 2
        assert data['valid'] is True

        # Step 3: Get suggested boxes
        response = client.post('/api/kits/wizard',
                             json={'step': 3},
                             headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['step'] == 3
        assert 'suggested_boxes' in data

        # Define custom boxes for step 4
        boxes_data = [
            {'box_number': '1', 'box_type': 'expendable', 'description': 'Expendables Box'},
            {'box_number': '2', 'box_type': 'tool', 'description': 'Tools Box'},
            {'box_number': '3', 'box_type': 'chemical', 'description': 'Chemicals Box'}
        ]

        # Step 4: Create the kit (use same kit_name from step 2)
        response = client.post('/api/kits/wizard',
                             json={
                                 'step': 4,
                                 'name': kit_name,
                                 'aircraft_type_id': aircraft_type.id,
                                 'description': 'Created via integration test',
                                 'boxes': boxes_data
                             },
                             headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)

        # Verify wizard completed
        assert data['step'] == 4
        assert data['complete'] is True
        assert 'kit' in data

        # Verify kit was created
        kit_data = data['kit']
        assert kit_data['name'] == kit_name
        assert kit_data['aircraft_type_id'] == aircraft_type.id
        assert kit_data['status'] == 'active'
        kit_id = kit_data['id']

        # Verify boxes were created
        boxes = KitBox.query.filter_by(kit_id=kit_id).all()
        assert len(boxes) == 3

        # Add expendable items to the kit
        box = boxes[0]  # Expendables box

        expendable_data = {
            'box_id': box.id,
            'part_number': 'EXP-001',
            'description': 'Safety Wire',
            'quantity': 100.0,
            'unit': 'ft',
            'minimum_stock_level': 50.0
        }

        response = client.post(f'/api/kits/{kit_id}/expendables',
                             json=expendable_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        json.loads(response.data)

        # Verify complete kit structure
        kit = Kit.query.get(kit_id)
        assert kit is not None
        assert kit.boxes.count() == 3
        assert kit.expendables.count() == 1


class TestIssuanceTriggeringReorder:
    """Test issuance workflow that triggers automatic reorder"""

    def test_issuance_triggers_automatic_reorder(self, client, auth_headers_materials, auth_headers_admin, aircraft_type, db_session):
        """Test that issuing items below minimum stock triggers automatic reorder"""

        # Create kit with expendable
        import uuid
        kit_name = f'Reorder Test Kit {uuid.uuid4().hex[:8]}'

        kit = Kit(
            name=kit_name,
            aircraft_type_id=aircraft_type.id,
            description='Test kit for reorder workflow',
            status='active',
            created_by=1
        )
        db_session.add(kit)
        db_session.flush()

        box = KitBox(
            kit_id=kit.id,
            box_number='1',
            box_type='expendable',
            description='Expendables'
        )
        db_session.add(box)
        db_session.flush()

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number='EXP-REORDER',
            description='Test Expendable',
            quantity=60.0,  # Just above minimum
            unit='ft',
            minimum_stock_level=50.0,  # Minimum stock level
            status='available'
        )
        db_session.add(expendable)
        db_session.commit()

        # Issue items to bring quantity below minimum
        issuance_data = {
            'item_type': 'expendable',
            'item_id': expendable.id,
            'quantity': 15.0,  # Will bring total to 45, below minimum of 50
            'purpose': 'Maintenance',
            'work_order': 'WO-12345'
        }

        response = client.post(f'/api/kits/{kit.id}/issue',
                             json=issuance_data,
                             headers=auth_headers_admin)

        assert response.status_code == 201
        issuance = json.loads(response.data)

        # Verify issuance was created
        assert issuance['quantity'] == 15.0
        assert issuance['item_id'] == expendable.id

        # Verify quantity was reduced
        db_session.refresh(expendable)
        assert expendable.quantity == 45.0
        assert expendable.status == 'low_stock'

        # Verify automatic reorder was created
        reorder = KitReorderRequest.query.filter_by(
            kit_id=kit.id,
            item_id=expendable.id,
            is_automatic=True
        ).first()

        assert reorder is not None
        assert reorder.status == 'pending'
        assert reorder.quantity_requested == 50.0  # Should request minimum_stock_level
        assert reorder.priority in ['medium', 'high']
        assert reorder.part_number == 'EXP-REORDER'


class TestTransferCompletingAndUpdatingInventory:
    """Test transfer workflow with inventory updates"""

    def test_transfer_workflow_updates_inventory(self, client, auth_headers_materials, aircraft_type, db_session):
        """Test complete transfer workflow from creation to completion"""

        # Create source kit with expendable
        import uuid
        source_kit = Kit(
            name=f'Source Kit {uuid.uuid4().hex[:8]}',
            aircraft_type_id=aircraft_type.id,
            description='Source kit',
            status='active',
            created_by=1
        )
        db_session.add(source_kit)
        db_session.flush()

        source_box = KitBox(
            kit_id=source_kit.id,
            box_number='1',
            box_type='expendable',
            description='Expendables'
        )
        db_session.add(source_box)
        db_session.flush()

        source_expendable = KitExpendable(
            kit_id=source_kit.id,
            box_id=source_box.id,
            part_number='EXP-TRANSFER',
            description='Transfer Test Item',
            quantity=100.0,
            unit='ea',
            status='available'
        )
        db_session.add(source_expendable)

        # Create destination kit
        dest_kit = Kit(
            name=f'Dest Kit {uuid.uuid4().hex[:8]}',
            aircraft_type_id=aircraft_type.id,
            description='Destination kit',
            status='active',
            created_by=1
        )
        db_session.add(dest_kit)
        db_session.commit()

        # Record initial quantity
        initial_quantity = source_expendable.quantity

        # Create transfer
        transfer_data = {
            'item_type': 'expendable',
            'item_id': source_expendable.id,
            'from_location_type': 'kit',
            'from_location_id': source_kit.id,
            'to_location_type': 'kit',
            'to_location_id': dest_kit.id,
            'quantity': 25.0,
            'notes': 'Integration test transfer'
        }

        response = client.post('/api/transfers',
                             json=transfer_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        transfer = json.loads(response.data)

        # Verify transfer was created
        assert transfer['status'] == 'pending'
        assert transfer['quantity'] == 25.0
        transfer_id = transfer['id']

        # Complete the transfer
        response = client.put(f'/api/transfers/{transfer_id}/complete',
                            headers=auth_headers_materials)

        assert response.status_code == 200
        completed_transfer = json.loads(response.data)

        # Verify transfer status updated
        assert completed_transfer['status'] == 'completed'
        assert completed_transfer['completed_date'] is not None

        # Verify source inventory was reduced
        db_session.refresh(source_expendable)
        assert source_expendable.quantity == initial_quantity - 25.0
        assert source_expendable.quantity == 75.0


class TestMessageThreadWorkflow:
    """Test message thread creation and replies"""

    def test_message_thread_workflow(self, client, auth_headers_admin, auth_headers_materials, aircraft_type, db_session):
        """Test creating a message thread with replies"""

        # Create kit
        import uuid
        kit = Kit(
            name=f'Message Test Kit {uuid.uuid4().hex[:8]}',
            aircraft_type_id=aircraft_type.id,
            description='Test kit for messaging',
            status='active',
            created_by=1
        )
        db_session.add(kit)
        db_session.commit()

        # Send initial message
        message_data = {
            'subject': 'Low Stock Alert',
            'message': 'We are running low on safety wire in this kit'
        }

        response = client.post(f'/api/kits/{kit.id}/messages',
                             json=message_data,
                             headers=auth_headers_admin)

        assert response.status_code == 201
        original_message = json.loads(response.data)

        # Verify message was created
        assert original_message['subject'] == 'Low Stock Alert'
        assert original_message['is_read'] is False
        message_id = original_message['id']

        # Reply to the message
        reply_data = {
            'message': 'I will send more safety wire today'
        }

        response = client.post(f'/api/messages/{message_id}/reply',
                             json=reply_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        reply = json.loads(response.data)

        # Verify reply was created
        assert reply['parent_message_id'] == message_id
        assert reply['subject'].startswith('Re:')
        assert reply['message'] == 'I will send more safety wire today'

        # Get original message with replies
        response = client.get(f'/api/messages/{message_id}',
                            headers=auth_headers_admin)

        assert response.status_code == 200
        message_with_replies = json.loads(response.data)

        # Verify thread structure
        assert message_with_replies['reply_count'] >= 1
        assert 'replies' in message_with_replies
        assert len(message_with_replies['replies']) >= 1

        # Mark original message as read
        response = client.put(f'/api/messages/{message_id}/read',
                            headers=auth_headers_admin)

        assert response.status_code == 200
        read_message = json.loads(response.data)

        # Verify read status
        assert read_message['is_read'] is True
        assert read_message['read_date'] is not None


class TestReorderApprovalFulfillmentWorkflow:
    """Test complete reorder workflow from creation to fulfillment"""

    def test_complete_reorder_workflow(self, client, auth_headers_admin, auth_headers_materials, aircraft_type, db_session):
        """Test reorder workflow: create -> approve -> order -> fulfill"""

        # Create kit with expendable
        import uuid
        kit = Kit(
            name=f'Reorder Workflow Kit {uuid.uuid4().hex[:8]}',
            aircraft_type_id=aircraft_type.id,
            description='Test kit for reorder workflow',
            status='active',
            created_by=1
        )
        db_session.add(kit)
        db_session.flush()

        box = KitBox(
            kit_id=kit.id,
            box_number='1',
            box_type='expendable',
            description='Expendables'
        )
        db_session.add(box)
        db_session.flush()

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number='EXP-WORKFLOW',
            description='Workflow Test Item',
            quantity=10.0,
            unit='ea',
            status='low_stock'
        )
        db_session.add(expendable)
        db_session.commit()

        initial_quantity = expendable.quantity

        # Step 1: Create reorder request
        reorder_data = {
            'item_type': 'expendable',
            'item_id': expendable.id,
            'part_number': 'EXP-WORKFLOW',
            'description': 'Workflow Test Item',
            'quantity_requested': 50.0,
            'priority': 'high',
            'notes': 'Urgent reorder needed'
        }

        response = client.post(f'/api/kits/{kit.id}/reorder',
                             json=reorder_data,
                             headers=auth_headers_admin)

        assert response.status_code == 201
        reorder = json.loads(response.data)

        # Verify reorder was created
        assert reorder['status'] == 'pending'
        assert reorder['quantity_requested'] == 50.0
        reorder_id = reorder['id']

        # Step 2: Approve the reorder (Materials user)
        response = client.put(f'/api/reorder-requests/{reorder_id}/approve',
                            headers=auth_headers_materials)

        assert response.status_code == 200
        approved_reorder = json.loads(response.data)

        # Verify approval
        assert approved_reorder['status'] == 'approved'
        assert approved_reorder['approved_by'] is not None
        assert approved_reorder['approved_date'] is not None

        # Step 3: Mark as ordered
        response = client.put(f'/api/reorder-requests/{reorder_id}/order',
                            headers=auth_headers_materials)

        assert response.status_code == 200
        ordered_reorder = json.loads(response.data)

        # Verify ordered status
        assert ordered_reorder['status'] == 'ordered'

        # Step 4: Fulfill the reorder
        response = client.put(f'/api/reorder-requests/{reorder_id}/fulfill',
                            headers=auth_headers_materials)

        assert response.status_code == 200
        fulfilled_reorder = json.loads(response.data)

        # Verify fulfillment
        assert fulfilled_reorder['status'] == 'fulfilled'
        assert fulfilled_reorder['fulfillment_date'] is not None

        # Verify inventory was updated
        db_session.refresh(expendable)
        assert expendable.quantity == initial_quantity + 50.0
        assert expendable.quantity == 60.0
        assert expendable.status == 'available'


class TestMultiStepKitOperations:
    """Test complex multi-step operations"""

    def test_kit_lifecycle_workflow(self, client, auth_headers_materials, auth_headers_admin, aircraft_type, db_session):
        """Test complete kit lifecycle: create -> add items -> issue -> transfer -> reorder"""

        # Step 1: Create kit
        import uuid
        kit_name = f'Lifecycle Kit {uuid.uuid4().hex[:8]}'

        kit_data = {
            'name': kit_name,
            'aircraft_type_id': aircraft_type.id,
            'description': 'Complete lifecycle test',
            'boxes': [
                {'box_number': '1', 'box_type': 'expendable', 'description': 'Expendables'}
            ]
        }

        response = client.post('/api/kits',
                             json=kit_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        kit = json.loads(response.data)
        kit_id = kit['id']

        # Step 2: Add expendable item
        boxes = KitBox.query.filter_by(kit_id=kit_id).all()
        box = boxes[0]

        expendable_data = {
            'box_id': box.id,
            'part_number': 'EXP-LIFECYCLE',
            'description': 'Lifecycle Test Item',
            'quantity': 100.0,
            'unit': 'ea',
            'minimum_stock_level': 30.0
        }

        response = client.post(f'/api/kits/{kit_id}/expendables',
                             json=expendable_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        expendable = json.loads(response.data)
        expendable_id = expendable['id']

        # Step 3: Issue items (should trigger reorder)
        issuance_data = {
            'item_type': 'expendable',
            'item_id': expendable_id,
            'quantity': 75.0,  # Brings to 25, below minimum of 30
            'purpose': 'Maintenance',
            'work_order': 'WO-LIFECYCLE'
        }

        response = client.post(f'/api/kits/{kit_id}/issue',
                             json=issuance_data,
                             headers=auth_headers_admin)

        assert response.status_code == 201

        # Verify automatic reorder was created
        reorder = KitReorderRequest.query.filter_by(
            kit_id=kit_id,
            item_id=expendable_id,
            is_automatic=True
        ).first()

        assert reorder is not None
        assert reorder.status == 'pending'

        # Step 4: Create second kit for transfer
        dest_kit_data = {
            'name': f'Dest Kit {uuid.uuid4().hex[:8]}',
            'aircraft_type_id': aircraft_type.id,
            'description': 'Transfer destination'
        }

        response = client.post('/api/kits',
                             json=dest_kit_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        dest_kit = json.loads(response.data)
        dest_kit_id = dest_kit['id']

        # Step 5: Transfer items between kits
        transfer_data = {
            'item_type': 'expendable',
            'item_id': expendable_id,
            'from_location_type': 'kit',
            'from_location_id': kit_id,
            'to_location_type': 'kit',
            'to_location_id': dest_kit_id,
            'quantity': 10.0
        }

        response = client.post('/api/transfers',
                             json=transfer_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        transfer = json.loads(response.data)

        # Complete the transfer
        response = client.put(f'/api/transfers/{transfer["id"]}/complete',
                            headers=auth_headers_materials)

        assert response.status_code == 200

        # Verify final state
        final_expendable = KitExpendable.query.get(expendable_id)
        assert final_expendable.quantity == 15.0  # 100 - 75 (issued) - 10 (transferred)

        # Verify kit has issuances, transfers, and reorders
        kit_obj = Kit.query.get(kit_id)
        assert kit_obj.issuances.count() >= 1
        assert kit_obj.reorder_requests.count() >= 1

        # Verify transfer exists
        transfer_obj = KitTransfer.query.get(transfer['id'])
        assert transfer_obj.status == 'completed'
