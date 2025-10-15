"""
Unit tests for Mobile Warehouse (Kits) models

Tests all kit-related models:
- AircraftType
- Kit
- KitBox
- KitItem
- KitExpendable
- KitIssuance
- KitTransfer
- KitReorderRequest
- KitMessage
"""

from models_kits import (
    AircraftType, Kit, KitBox, KitExpendable, KitIssuance,
    KitTransfer, KitReorderRequest, KitMessage
)


def get_or_create_aircraft_type(db_session, name):
    """Helper function to get or create an aircraft type"""
    aircraft_type = AircraftType.query.filter_by(name=name).first()
    if not aircraft_type:
        aircraft_type = AircraftType(name=name, is_active=True)
        db_session.add(aircraft_type)
        db_session.commit()
    return aircraft_type


class TestAircraftTypeModel:
    """Test AircraftType model functionality"""

    def test_create_aircraft_type(self, db_session):
        """Test creating an aircraft type"""
        aircraft_type = AircraftType(
            name='Q400',
            description='Bombardier Q400 turboprop',
            is_active=True
        )

        db_session.add(aircraft_type)
        db_session.commit()

        assert aircraft_type.id is not None
        assert aircraft_type.name == 'Q400'
        assert aircraft_type.description == 'Bombardier Q400 turboprop'
        assert aircraft_type.is_active is True
        assert aircraft_type.created_at is not None

    def test_aircraft_type_to_dict(self, db_session):
        """Test aircraft type to_dict method"""
        aircraft_type = AircraftType(
            name='RJ85',
            description='British Aerospace RJ85',
            is_active=True
        )
        db_session.add(aircraft_type)
        db_session.commit()

        data = aircraft_type.to_dict()

        assert data['id'] == aircraft_type.id
        assert data['name'] == 'RJ85'
        assert data['description'] == 'British Aerospace RJ85'
        assert data['is_active'] is True
        assert 'created_at' in data

    def test_aircraft_type_deactivation(self, db_session):
        """Test deactivating an aircraft type"""
        aircraft_type = AircraftType(
            name='CL415',
            description='Canadair CL-415',
            is_active=True
        )
        db_session.add(aircraft_type)
        db_session.commit()

        # Deactivate
        aircraft_type.is_active = False
        db_session.commit()

        assert aircraft_type.is_active is False


class TestKitModel:
    """Test Kit model functionality"""

    def test_create_kit(self, db_session, admin_user):
        """Test creating a kit"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        kit = Kit(
            name='Q400-Kit-Alpha',
            aircraft_type_id=aircraft_type.id,
            description='Primary Q400 maintenance kit',
            status='active',
            created_by=admin_user.id
        )

        db_session.add(kit)
        db_session.commit()

        assert kit.id is not None
        assert kit.name == 'Q400-Kit-Alpha'
        assert kit.aircraft_type_id == aircraft_type.id
        assert kit.status == 'active'
        assert kit.created_by == admin_user.id
        assert kit.created_at is not None
        assert kit.updated_at is not None

    def test_kit_to_dict(self, db_session, admin_user):
        """Test kit to_dict method"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'RJ85')

        kit = Kit(
            name='RJ85-Kit-Main',
            aircraft_type_id=aircraft_type.id,
            description='Main RJ85 kit',
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit)
        db_session.commit()

        data = kit.to_dict()

        assert data['id'] == kit.id
        assert data['name'] == 'RJ85-Kit-Main'
        assert data['aircraft_type_id'] == aircraft_type.id
        assert data['status'] == 'active'
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_kit_status_values(self, db_session, admin_user):
        """Test kit status values"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        # Test active status
        kit_active = Kit(
            name='Active Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit_active)

        # Test inactive status
        kit_inactive = Kit(
            name='Inactive Kit',
            aircraft_type_id=aircraft_type.id,
            status='inactive',
            created_by=admin_user.id
        )
        db_session.add(kit_inactive)

        # Test maintenance status
        kit_maintenance = Kit(
            name='Maintenance Kit',
            aircraft_type_id=aircraft_type.id,
            status='maintenance',
            created_by=admin_user.id
        )
        db_session.add(kit_maintenance)

        db_session.commit()

        assert kit_active.status == 'active'
        assert kit_inactive.status == 'inactive'
        assert kit_maintenance.status == 'maintenance'

    def test_kit_aircraft_type_relationship(self, db_session, admin_user):
        """Test kit relationship with aircraft type"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'CL415')

        kit = Kit(
            name='CL415-Kit-Fire',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit)
        db_session.commit()

        # Test relationship
        assert kit.aircraft_type.name == 'CL415'
        assert aircraft_type.kits[0].name == 'CL415-Kit-Fire'


class TestKitBoxModel:
    """Test KitBox model functionality"""

    def test_create_kit_box(self, db_session, admin_user):
        """Test creating a kit box"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        kit = Kit(
            name='Test Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit)
        db_session.commit()

        box = KitBox(
            kit_id=kit.id,
            box_number=1,
            box_type='expendable',
            description='Expendable items box'
        )

        db_session.add(box)
        db_session.commit()

        assert box.id is not None
        assert box.kit_id == kit.id
        assert box.box_number == 1
        assert box.box_type == 'expendable'
        assert box.description == 'Expendable items box'
        assert box.created_at is not None

    def test_kit_box_types(self, db_session, admin_user):
        """Test all kit box types"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        kit = Kit(
            name='Test Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit)
        db_session.commit()

        box_types = ['expendable', 'tooling', 'consumable', 'loose', 'floor']

        for i, box_type in enumerate(box_types, 1):
            box = KitBox(
                kit_id=kit.id,
                box_number=i,
                box_type=box_type,
                description=f'{box_type.capitalize()} box'
            )
            db_session.add(box)

        db_session.commit()

        boxes = KitBox.query.filter_by(kit_id=kit.id).all()
        assert len(boxes) == 5

        box_type_names = [box.box_type for box in boxes]
        assert set(box_type_names) == set(box_types)

    def test_kit_box_relationship(self, db_session, admin_user):
        """Test kit box relationship with kit"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        kit = Kit(
            name='Test Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit)
        db_session.commit()

        box = KitBox(
            kit_id=kit.id,
            box_number=1,
            box_type='tooling',
            description='Tooling box'
        )
        db_session.add(box)
        db_session.commit()

        # Test relationship
        assert box.kit.name == 'Test Kit'
        assert kit.boxes[0].box_type == 'tooling'


class TestKitExpendableModel:
    """Test KitExpendable model functionality"""

    def test_create_kit_expendable(self, db_session, admin_user):
        """Test creating a kit expendable"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        kit = Kit(
            name='Test Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit)
        db_session.commit()

        box = KitBox(
            kit_id=kit.id,
            box_number=1,
            box_type='expendable'
        )
        db_session.add(box)
        db_session.commit()

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number='EXP-001',
            description='Safety Wire',
            quantity=100,
            unit='ft',
            location='Box 1',
            status='available',
            minimum_stock_level=25
        )

        db_session.add(expendable)
        db_session.commit()

        assert expendable.id is not None
        assert expendable.part_number == 'EXP-001'
        assert expendable.quantity == 100
        assert expendable.unit == 'ft'
        assert expendable.status == 'available'
        assert expendable.minimum_stock_level == 25

    def test_kit_expendable_to_dict(self, db_session, admin_user):
        """Test kit expendable to_dict method"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        kit = Kit(
            name='Test Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit)
        db_session.commit()

        box = KitBox(kit_id=kit.id, box_number=1, box_type='expendable')
        db_session.add(box)
        db_session.commit()

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number='EXP-002',
            description='Cleaning Rags',
            quantity=50,
            unit='ea',
            location='Box 1',
            status='available'
        )
        db_session.add(expendable)
        db_session.commit()

        data = expendable.to_dict()

        assert data['id'] == expendable.id
        assert data['part_number'] == 'EXP-002'
        assert data['description'] == 'Cleaning Rags'
        assert data['quantity'] == 50
        assert data['unit'] == 'ea'
        assert data['status'] == 'available'


class TestKitIssuanceModel:
    """Test KitIssuance model functionality"""

    def test_create_kit_issuance(self, db_session, admin_user):
        """Test creating a kit issuance"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        kit = Kit(
            name='Test Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit)
        db_session.commit()

        box = KitBox(kit_id=kit.id, box_number=1, box_type='expendable')
        db_session.add(box)
        db_session.commit()

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number='EXP-001',
            description='Safety Wire',
            quantity=100,
            unit='ft',
            status='available'
        )
        db_session.add(expendable)
        db_session.commit()

        issuance = KitIssuance(
            kit_id=kit.id,
            item_type='expendable',
            item_id=expendable.id,
            issued_by=admin_user.id,
            quantity=10,
            purpose='Maintenance',
            work_order='WO-12345',
            notes='Routine maintenance'
        )

        db_session.add(issuance)
        db_session.commit()

        assert issuance.id is not None
        assert issuance.kit_id == kit.id
        assert issuance.item_type == 'expendable'
        assert issuance.item_id == expendable.id
        assert issuance.issued_by == admin_user.id
        assert issuance.quantity == 10
        assert issuance.purpose == 'Maintenance'
        assert issuance.work_order == 'WO-12345'
        assert issuance.issued_date is not None

    def test_kit_issuance_to_dict(self, db_session, admin_user):
        """Test kit issuance to_dict method"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        kit = Kit(
            name='Test Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit)
        db_session.commit()

        box = KitBox(kit_id=kit.id, box_number=1, box_type='expendable')
        db_session.add(box)
        db_session.commit()

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number='EXP-001',
            description='Safety Wire',
            quantity=100,
            unit='ft',
            status='available'
        )
        db_session.add(expendable)
        db_session.commit()

        issuance = KitIssuance(
            kit_id=kit.id,
            item_type='expendable',
            item_id=expendable.id,
            issued_by=admin_user.id,
            quantity=5,
            purpose='Repair'
        )
        db_session.add(issuance)
        db_session.commit()

        data = issuance.to_dict()

        assert data['id'] == issuance.id
        assert data['kit_id'] == kit.id
        assert data['item_type'] == 'expendable'
        assert data['quantity'] == 5
        assert data['purpose'] == 'Repair'


class TestKitTransferModel:
    """Test KitTransfer model functionality"""

    def test_create_kit_transfer(self, db_session, admin_user):
        """Test creating a kit transfer"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        kit1 = Kit(
            name='Source Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        kit2 = Kit(
            name='Destination Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add_all([kit1, kit2])
        db_session.commit()

        box = KitBox(kit_id=kit1.id, box_number=1, box_type='expendable')
        db_session.add(box)
        db_session.commit()

        expendable = KitExpendable(
            kit_id=kit1.id,
            box_id=box.id,
            part_number='EXP-001',
            description='Safety Wire',
            quantity=100,
            unit='ft',
            status='available'
        )
        db_session.add(expendable)
        db_session.commit()

        transfer = KitTransfer(
            item_type='expendable',
            item_id=expendable.id,
            from_location_type='kit',
            from_location_id=kit1.id,
            to_location_type='kit',
            to_location_id=kit2.id,
            quantity=20,
            transferred_by=admin_user.id,
            status='pending',
            notes='Transfer for remote operation'
        )

        db_session.add(transfer)
        db_session.commit()

        assert transfer.id is not None
        assert transfer.from_location_type == 'kit'
        assert transfer.from_location_id == kit1.id
        assert transfer.to_location_type == 'kit'
        assert transfer.to_location_id == kit2.id
        assert transfer.quantity == 20
        assert transfer.status == 'pending'
        assert transfer.transfer_date is not None

    def test_kit_transfer_status_values(self, db_session, admin_user):
        """Test kit transfer status values"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        kit = Kit(
            name='Test Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit)
        db_session.commit()

        box = KitBox(kit_id=kit.id, box_number=1, box_type='expendable')
        db_session.add(box)
        db_session.commit()

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number='EXP-001',
            description='Safety Wire',
            quantity=100,
            unit='ft',
            status='available'
        )
        db_session.add(expendable)
        db_session.commit()

        # Test pending status
        transfer_pending = KitTransfer(
            item_type='expendable',
            item_id=expendable.id,
            from_location_type='kit',
            from_location_id=kit.id,
            to_location_type='warehouse',
            to_location_id=1,
            quantity=10,
            transferred_by=admin_user.id,
            status='pending'
        )
        db_session.add(transfer_pending)

        # Test completed status
        transfer_completed = KitTransfer(
            item_type='expendable',
            item_id=expendable.id,
            from_location_type='kit',
            from_location_id=kit.id,
            to_location_type='warehouse',
            to_location_id=1,
            quantity=10,
            transferred_by=admin_user.id,
            status='completed'
        )
        db_session.add(transfer_completed)

        # Test cancelled status
        transfer_cancelled = KitTransfer(
            item_type='expendable',
            item_id=expendable.id,
            from_location_type='kit',
            from_location_id=kit.id,
            to_location_type='warehouse',
            to_location_id=1,
            quantity=10,
            transferred_by=admin_user.id,
            status='cancelled'
        )
        db_session.add(transfer_cancelled)

        db_session.commit()

        assert transfer_pending.status == 'pending'
        assert transfer_completed.status == 'completed'
        assert transfer_cancelled.status == 'cancelled'


class TestKitReorderRequestModel:
    """Test KitReorderRequest model functionality"""

    def test_create_reorder_request(self, db_session, admin_user):
        """Test creating a reorder request"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        kit = Kit(
            name='Test Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit)
        db_session.commit()

        box = KitBox(kit_id=kit.id, box_number=1, box_type='expendable')
        db_session.add(box)
        db_session.commit()

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number='EXP-001',
            description='Safety Wire',
            quantity=10,
            unit='ft',
            status='available'
        )
        db_session.add(expendable)
        db_session.commit()

        reorder = KitReorderRequest(
            kit_id=kit.id,
            item_type='expendable',
            item_id=expendable.id,
            part_number='EXP-001',
            description='Safety Wire',
            quantity_requested=100,
            priority='high',
            requested_by=admin_user.id,
            status='pending',
            notes='Low stock - urgent reorder needed'
        )

        db_session.add(reorder)
        db_session.commit()

        assert reorder.id is not None
        assert reorder.kit_id == kit.id
        assert reorder.item_type == 'expendable'
        assert reorder.quantity_requested == 100
        assert reorder.priority == 'high'
        assert reorder.status == 'pending'
        assert reorder.requested_date is not None

    def test_reorder_priority_levels(self, db_session, admin_user):
        """Test reorder request priority levels"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        kit = Kit(
            name='Test Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit)
        db_session.commit()

        box = KitBox(kit_id=kit.id, box_number=1, box_type='expendable')
        db_session.add(box)
        db_session.commit()

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number='EXP-001',
            description='Safety Wire',
            quantity=10,
            unit='ft',
            status='available'
        )
        db_session.add(expendable)
        db_session.commit()

        priorities = ['low', 'medium', 'high', 'urgent']

        for priority in priorities:
            reorder = KitReorderRequest(
                kit_id=kit.id,
                item_type='expendable',
                item_id=expendable.id,
                part_number='EXP-001',
                description='Safety Wire',
                quantity_requested=50,
                priority=priority,
                requested_by=admin_user.id,
                status='pending'
            )
            db_session.add(reorder)

        db_session.commit()

        reorders = KitReorderRequest.query.filter_by(kit_id=kit.id).all()
        assert len(reorders) == 4

        priority_values = [r.priority for r in reorders]
        assert set(priority_values) == set(priorities)

    def test_reorder_status_values(self, db_session, admin_user):
        """Test reorder request status values"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        kit = Kit(
            name='Test Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit)
        db_session.commit()

        box = KitBox(kit_id=kit.id, box_number=1, box_type='expendable')
        db_session.add(box)
        db_session.commit()

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number='EXP-001',
            description='Safety Wire',
            quantity=10,
            unit='ft',
            status='available'
        )
        db_session.add(expendable)
        db_session.commit()

        statuses = ['pending', 'approved', 'ordered', 'fulfilled', 'cancelled']

        for status in statuses:
            reorder = KitReorderRequest(
                kit_id=kit.id,
                item_type='expendable',
                item_id=expendable.id,
                part_number='EXP-001',
                description='Safety Wire',
                quantity_requested=50,
                priority='medium',
                requested_by=admin_user.id,
                status=status
            )
            db_session.add(reorder)

        db_session.commit()

        reorders = KitReorderRequest.query.filter_by(kit_id=kit.id).all()
        assert len(reorders) == 5

        status_values = [r.status for r in reorders]
        assert set(status_values) == set(statuses)


class TestKitMessageModel:
    """Test KitMessage model functionality"""

    def test_create_kit_message(self, db_session, admin_user, regular_user):
        """Test creating a kit message"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        kit = Kit(
            name='Test Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit)
        db_session.commit()

        message = KitMessage(
            kit_id=kit.id,
            sender_id=regular_user.id,
            recipient_id=admin_user.id,
            subject='Low stock alert',
            message='Safety wire is running low. Please reorder.',
            is_read=False
        )

        db_session.add(message)
        db_session.commit()

        assert message.id is not None
        assert message.kit_id == kit.id
        assert message.sender_id == regular_user.id
        assert message.recipient_id == admin_user.id
        assert message.subject == 'Low stock alert'
        assert message.is_read is False
        assert message.sent_date is not None

    def test_kit_message_broadcast(self, db_session, admin_user):
        """Test broadcast message (no specific recipient)"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        kit = Kit(
            name='Test Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit)
        db_session.commit()

        message = KitMessage(
            kit_id=kit.id,
            sender_id=admin_user.id,
            recipient_id=None,  # Broadcast message
            subject='Kit maintenance scheduled',
            message='This kit will undergo maintenance next week.',
            is_read=False
        )

        db_session.add(message)
        db_session.commit()

        assert message.recipient_id is None
        assert message.subject == 'Kit maintenance scheduled'

    def test_kit_message_threading(self, db_session, admin_user, regular_user):
        """Test message threading"""
        aircraft_type = get_or_create_aircraft_type(db_session, 'Q400')

        kit = Kit(
            name='Test Kit',
            aircraft_type_id=aircraft_type.id,
            status='active',
            created_by=admin_user.id
        )
        db_session.add(kit)
        db_session.commit()

        # Original message
        original_message = KitMessage(
            kit_id=kit.id,
            sender_id=regular_user.id,
            recipient_id=admin_user.id,
            subject='Reorder request',
            message='Need more safety wire',
            is_read=False
        )
        db_session.add(original_message)
        db_session.commit()

        # Reply message
        reply_message = KitMessage(
            kit_id=kit.id,
            sender_id=admin_user.id,
            recipient_id=regular_user.id,
            subject='Re: Reorder request',
            message='Approved. Will order today.',
            is_read=False,
            parent_message_id=original_message.id
        )
        db_session.add(reply_message)
        db_session.commit()

        assert reply_message.parent_message_id == original_message.id
        assert original_message.replies[0].id == reply_message.id
