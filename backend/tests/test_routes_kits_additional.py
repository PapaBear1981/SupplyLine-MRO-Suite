"""
Additional unit tests for Kit API endpoints to improve coverage.

Tests cover:
- Kit wizard steps 3 and 4
- Kit creation with boxes
- Aircraft type validation scenarios
- Kit item error handling
- Expendable management edge cases
- Issuance with automatic reorders
- Analytics and reporting filters
- Recent activity tracking
"""

import json
import uuid
from datetime import datetime, timedelta

import pytest

from models import Chemical, Tool, User, Warehouse
from models_kits import (
    AircraftType,
    Kit,
    KitBox,
    KitExpendable,
    KitIssuance,
    KitItem,
    KitMessage,
    KitReorderRequest,
    KitTransfer,
)


# ==================== Fixtures ====================

@pytest.fixture
def aircraft_type(db_session):
    """Create a test aircraft type"""
    at = AircraftType(
        name=f"Q400-{uuid.uuid4().hex[:6]}",
        description="Test Aircraft",
        is_active=True
    )
    db_session.add(at)
    db_session.commit()
    return at


@pytest.fixture
def test_kit_with_box(db_session, materials_user, aircraft_type):
    """Create a test kit with a box"""
    kit = Kit(
        name=f"TestKit-{uuid.uuid4().hex[:8]}",
        aircraft_type_id=aircraft_type.id,
        description="Test kit with box",
        status="active",
        created_by=materials_user.id
    )
    db_session.add(kit)
    db_session.flush()

    box = KitBox(
        kit_id=kit.id,
        box_number="Box1",
        box_type="expendable",
        description="Expendable items box"
    )
    db_session.add(box)
    db_session.commit()
    return kit, box


@pytest.fixture
def test_warehouse_for_kits(db_session):
    """Create a test warehouse for kit item transfers"""
    warehouse = Warehouse(
        name=f"Warehouse-{uuid.uuid4().hex[:6]}",
        address="456 Test Ave",
        is_active=True
    )
    db_session.add(warehouse)
    db_session.commit()
    return warehouse


@pytest.fixture
def test_tool_in_warehouse(db_session, test_warehouse_for_kits):
    """Create a tool in a warehouse"""
    tool = Tool(
        tool_number=f"T-{uuid.uuid4().hex[:6]}",
        serial_number=f"SN-{uuid.uuid4().hex[:8]}",
        description="Test Tool in Warehouse",
        condition="Good",
        location="Test Location",
        category="Hand Tools",
        warehouse_id=test_warehouse_for_kits.id,
        status="available"
    )
    db_session.add(tool)
    db_session.commit()
    return tool


@pytest.fixture
def test_chemical_in_warehouse(db_session, test_warehouse_for_kits):
    """Create a chemical in a warehouse"""
    chemical = Chemical(
        part_number=f"C-{uuid.uuid4().hex[:6]}",
        lot_number=f"L-{uuid.uuid4().hex[:8]}",
        description="Test Chemical in Warehouse",
        manufacturer="Test Manufacturer",
        quantity=100.0,
        unit="ml",
        location="Chemical Storage",
        category="Solvents",
        warehouse_id=test_warehouse_for_kits.id,
        status="available"
    )
    db_session.add(chemical)
    db_session.commit()
    return chemical


# ==================== Kit Wizard Tests ====================

class TestKitWizardAdditional:
    """Additional tests for kit wizard endpoints"""

    def test_kit_wizard_step3_box_configuration(self, client, auth_headers_materials, aircraft_type):
        """Test kit wizard step 3 - box configuration"""
        wizard_data = {
            "step": 3,
            "aircraft_type_id": aircraft_type.id,
            "name": "Step3 Kit"
        }

        response = client.post("/api/kits/wizard",
                             json=wizard_data,
                             headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["step"] == 3
        assert "suggested_boxes" in data
        assert isinstance(data["suggested_boxes"], list)
        assert len(data["suggested_boxes"]) == 5
        assert data["next_step"] == 4

        # Verify suggested box types
        box_types = [box["box_type"] for box in data["suggested_boxes"]]
        assert "expendable" in box_types
        assert "tooling" in box_types
        assert "consumable" in box_types
        assert "loose" in box_types
        assert "floor" in box_types

    def test_kit_wizard_step4_complete_creation(self, client, auth_headers_materials, aircraft_type, db_session):
        """Test kit wizard step 4 - complete kit creation"""
        kit_name = f"Wizard Kit {uuid.uuid4().hex[:8]}"
        wizard_data = {
            "step": 4,
            "aircraft_type_id": aircraft_type.id,
            "name": kit_name,
            "description": "Created via wizard step 4",
            "boxes": [
                {"box_number": "Box1", "box_type": "expendable", "description": "Expendables"},
                {"box_number": "Box2", "box_type": "tooling", "description": "Tools"}
            ]
        }

        response = client.post("/api/kits/wizard",
                             json=wizard_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data["step"] == 4
        assert data["complete"] is True
        assert "kit" in data
        assert data["kit"]["name"] == kit_name
        assert data["kit"]["description"] == "Created via wizard step 4"

        # Verify kit and boxes were created in database
        kit = Kit.query.filter_by(name=kit_name).first()
        assert kit is not None
        assert kit.boxes.count() == 2

    def test_kit_wizard_step4_missing_fields(self, client, auth_headers_materials):
        """Test kit wizard step 4 with missing required fields"""
        wizard_data = {
            "step": 4,
            "description": "Missing name and aircraft_type_id"
        }

        response = client.post("/api/kits/wizard",
                             json=wizard_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "missing" in data["error"].lower() or "required" in data["error"].lower()

    def test_kit_wizard_step2_duplicate_name(self, client, auth_headers_materials, aircraft_type, test_kit_with_box):
        """Test kit wizard step 2 with duplicate kit name"""
        kit, _ = test_kit_with_box
        wizard_data = {
            "step": 2,
            "aircraft_type_id": aircraft_type.id,
            "name": kit.name  # Use existing kit name
        }

        response = client.post("/api/kits/wizard",
                             json=wizard_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "already exists" in data["error"]

    def test_kit_wizard_step2_missing_name(self, client, auth_headers_materials, aircraft_type):
        """Test kit wizard step 2 without kit name"""
        wizard_data = {
            "step": 2,
            "aircraft_type_id": aircraft_type.id
        }

        response = client.post("/api/kits/wizard",
                             json=wizard_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_kit_wizard_step2_missing_aircraft_type(self, client, auth_headers_materials):
        """Test kit wizard step 2 without aircraft type"""
        wizard_data = {
            "step": 2,
            "name": "New Kit"
        }

        response = client.post("/api/kits/wizard",
                             json=wizard_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_kit_wizard_invalid_step(self, client, auth_headers_materials):
        """Test kit wizard with invalid step number"""
        wizard_data = {
            "step": 99
        }

        response = client.post("/api/kits/wizard",
                             json=wizard_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "invalid" in data["error"].lower()


# ==================== Aircraft Type Tests ====================

class TestAircraftTypeAdditional:
    """Additional tests for aircraft type endpoints"""

    def test_update_aircraft_type_name_duplicate(self, client, auth_headers_admin, db_session):
        """Test updating aircraft type name to a duplicate"""
        at1 = AircraftType(name=f"Type1-{uuid.uuid4().hex[:6]}", is_active=True)
        at2 = AircraftType(name=f"Type2-{uuid.uuid4().hex[:6]}", is_active=True)
        db_session.add(at1)
        db_session.add(at2)
        db_session.commit()

        # Try to rename at2 to at1's name
        update_data = {"name": at1.name}

        response = client.put(f"/api/aircraft-types/{at2.id}",
                            json=update_data,
                            headers=auth_headers_admin)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "already exists" in data["error"]

    def test_update_aircraft_type_name_success(self, client, auth_headers_admin, db_session):
        """Test successfully updating aircraft type name"""
        at = AircraftType(
            name=f"OldName-{uuid.uuid4().hex[:6]}",
            description="Original description",
            is_active=True
        )
        db_session.add(at)
        db_session.commit()

        new_name = f"NewName-{uuid.uuid4().hex[:6]}"
        update_data = {"name": new_name}

        response = client.put(f"/api/aircraft-types/{at.id}",
                            json=update_data,
                            headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == new_name

    def test_deactivate_aircraft_type_with_active_kits(self, client, auth_headers_admin, db_session, materials_user):
        """Test deactivating aircraft type that has active kits (should fail)"""
        at = AircraftType(
            name=f"ActiveType-{uuid.uuid4().hex[:6]}",
            is_active=True
        )
        db_session.add(at)
        db_session.flush()

        # Create active kit referencing this aircraft type
        kit = Kit(
            name=f"ActiveKit-{uuid.uuid4().hex[:8]}",
            aircraft_type_id=at.id,
            status="active",
            created_by=materials_user.id
        )
        db_session.add(kit)
        db_session.commit()

        response = client.delete(f"/api/aircraft-types/{at.id}",
                               headers=auth_headers_admin)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "active kits" in data["error"].lower()


# ==================== Kit CRUD Tests ====================

class TestKitCRUDAdditional:
    """Additional tests for kit CRUD operations"""

    def test_create_kit_with_boxes(self, client, auth_headers_materials, aircraft_type, db_session):
        """Test creating kit with boxes in single request"""
        kit_name = f"KitWithBoxes-{uuid.uuid4().hex[:8]}"
        kit_data = {
            "name": kit_name,
            "aircraft_type_id": aircraft_type.id,
            "description": "Kit with boxes",
            "boxes": [
                {"box_number": "Box1", "box_type": "expendable", "description": "Expendables"},
                {"box_number": "Box2", "box_type": "tooling", "description": "Tools"},
                {"box_number": "Loose", "box_type": "loose", "description": "Loose items"}
            ]
        }

        response = client.post("/api/kits",
                             json=kit_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["name"] == kit_name

        # Verify boxes were created
        kit = Kit.query.filter_by(name=kit_name).first()
        assert kit is not None
        assert kit.boxes.count() == 3

    def test_create_kit_invalid_aircraft_type(self, client, auth_headers_materials):
        """Test creating kit with non-existent aircraft type"""
        kit_data = {
            "name": f"InvalidKit-{uuid.uuid4().hex[:8]}",
            "aircraft_type_id": 99999
        }

        response = client.post("/api/kits",
                             json=kit_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "invalid" in data["error"].lower()

    def test_create_kit_duplicate_name(self, client, auth_headers_materials, test_kit_with_box):
        """Test creating kit with duplicate name"""
        kit, _ = test_kit_with_box
        kit_data = {
            "name": kit.name,
            "aircraft_type_id": kit.aircraft_type_id
        }

        response = client.post("/api/kits",
                             json=kit_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "already exists" in data["error"]

    def test_update_kit_name_duplicate(self, client, auth_headers_materials, db_session, aircraft_type, materials_user):
        """Test updating kit name to a duplicate"""
        kit1 = Kit(
            name=f"Kit1-{uuid.uuid4().hex[:8]}",
            aircraft_type_id=aircraft_type.id,
            status="active",
            created_by=materials_user.id
        )
        kit2 = Kit(
            name=f"Kit2-{uuid.uuid4().hex[:8]}",
            aircraft_type_id=aircraft_type.id,
            status="active",
            created_by=materials_user.id
        )
        db_session.add(kit1)
        db_session.add(kit2)
        db_session.commit()

        update_data = {"name": kit1.name}

        response = client.put(f"/api/kits/{kit2.id}",
                            json=update_data,
                            headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "already exists" in data["error"]

    def test_delete_kit_with_active_items(self, client, auth_headers_materials, db_session, test_kit_with_box):
        """Test deleting kit with active items (should fail)"""
        kit, box = test_kit_with_box

        # Add an available item to the kit
        kit_item = KitItem(
            kit_id=kit.id,
            box_id=box.id,
            item_type="tool",
            item_id=1,
            part_number="T-001",
            description="Test tool",
            quantity=1,
            status="available"
        )
        db_session.add(kit_item)
        db_session.commit()

        response = client.delete(f"/api/kits/{kit.id}",
                               headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "active items" in data["error"].lower()

    def test_duplicate_kit_with_custom_description(self, client, auth_headers_materials, test_kit_with_box):
        """Test duplicating kit with custom description"""
        kit, box = test_kit_with_box
        new_name = f"Duplicated-{uuid.uuid4().hex[:8]}"
        duplicate_data = {
            "name": new_name,
            "description": "Custom description for duplicate"
        }

        response = client.post(f"/api/kits/{kit.id}/duplicate",
                             json=duplicate_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["name"] == new_name
        assert data["description"] == "Custom description for duplicate"

    def test_duplicate_kit_missing_name(self, client, auth_headers_materials, test_kit_with_box):
        """Test duplicating kit without new name (should fail)"""
        kit, _ = test_kit_with_box
        duplicate_data = {}

        response = client.post(f"/api/kits/{kit.id}/duplicate",
                             json=duplicate_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_duplicate_kit_duplicate_name(self, client, auth_headers_materials, test_kit_with_box):
        """Test duplicating kit with existing name (should fail)"""
        kit, _ = test_kit_with_box
        duplicate_data = {"name": kit.name}

        response = client.post(f"/api/kits/{kit.id}/duplicate",
                             json=duplicate_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_get_kits_with_status_filter(self, client, auth_headers_user, db_session, aircraft_type, materials_user):
        """Test getting kits with status filter"""
        # Create kits with different statuses
        active_kit = Kit(
            name=f"Active-{uuid.uuid4().hex[:8]}",
            aircraft_type_id=aircraft_type.id,
            status="active",
            created_by=materials_user.id
        )
        inactive_kit = Kit(
            name=f"Inactive-{uuid.uuid4().hex[:8]}",
            aircraft_type_id=aircraft_type.id,
            status="inactive",
            created_by=materials_user.id
        )
        db_session.add(active_kit)
        db_session.add(inactive_kit)
        db_session.commit()

        response = client.get("/api/kits?status=active", headers=auth_headers_user)
        assert response.status_code == 200
        data = json.loads(response.data)
        # All returned kits should be active
        for kit in data:
            assert kit["status"] == "active"

    def test_get_kits_with_aircraft_type_filter(self, client, auth_headers_user, db_session, aircraft_type, materials_user):
        """Test getting kits with aircraft type filter"""
        kit = Kit(
            name=f"FilterTest-{uuid.uuid4().hex[:8]}",
            aircraft_type_id=aircraft_type.id,
            status="active",
            created_by=materials_user.id
        )
        db_session.add(kit)
        db_session.commit()

        response = client.get(f"/api/kits?aircraft_type_id={aircraft_type.id}", headers=auth_headers_user)
        assert response.status_code == 200
        data = json.loads(response.data)
        for kit_data in data:
            assert kit_data["aircraft_type_id"] == aircraft_type.id


# ==================== Kit Box Tests ====================

class TestKitBoxAdditional:
    """Additional tests for kit box management"""

    def test_add_box_missing_box_number(self, client, auth_headers_materials, test_kit_with_box):
        """Test adding box without box number (should fail)"""
        kit, _ = test_kit_with_box
        box_data = {
            "box_type": "tooling"
        }

        response = client.post(f"/api/kits/{kit.id}/boxes",
                             json=box_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_add_box_missing_box_type(self, client, auth_headers_materials, test_kit_with_box):
        """Test adding box without box type (should fail)"""
        kit, _ = test_kit_with_box
        box_data = {
            "box_number": "Box99"
        }

        response = client.post(f"/api/kits/{kit.id}/boxes",
                             json=box_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_add_box_duplicate_number(self, client, auth_headers_materials, test_kit_with_box):
        """Test adding box with duplicate number (should fail)"""
        kit, box = test_kit_with_box
        box_data = {
            "box_number": box.box_number,
            "box_type": "tooling"
        }

        response = client.post(f"/api/kits/{kit.id}/boxes",
                             json=box_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "already exists" in data["error"]

    def test_update_box_number_duplicate(self, client, auth_headers_materials, db_session, test_kit_with_box):
        """Test updating box number to duplicate (should fail)"""
        kit, box1 = test_kit_with_box

        box2 = KitBox(
            kit_id=kit.id,
            box_number="Box2",
            box_type="tooling",
            description="Second box"
        )
        db_session.add(box2)
        db_session.commit()

        update_data = {"box_number": box1.box_number}

        response = client.put(f"/api/kits/{kit.id}/boxes/{box2.id}",
                            json=update_data,
                            headers=auth_headers_materials)

        assert response.status_code == 400

    def test_update_box_type_and_description(self, client, auth_headers_materials, test_kit_with_box):
        """Test updating box type and description"""
        kit, box = test_kit_with_box
        update_data = {
            "box_type": "consumable",
            "description": "Updated description"
        }

        response = client.put(f"/api/kits/{kit.id}/boxes/{box.id}",
                            json=update_data,
                            headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["box_type"] == "consumable"
        assert data["description"] == "Updated description"

    def test_delete_box_with_items(self, client, auth_headers_materials, db_session, test_kit_with_box):
        """Test deleting box that contains items (should fail)"""
        kit, box = test_kit_with_box

        # Add an expendable to the box
        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number="EXP-001",
            description="Test expendable",
            quantity=10,
            unit="ea",
            status="available"
        )
        db_session.add(expendable)
        db_session.commit()

        response = client.delete(f"/api/kits/{kit.id}/boxes/{box.id}",
                               headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "items" in data["error"].lower()


# ==================== Kit Item Tests ====================

class TestKitItemAdditional:
    """Additional tests for kit item management"""

    def test_add_item_missing_box_id(self, client, auth_headers_materials, test_kit_with_box):
        """Test adding item without box ID (should fail)"""
        kit, _ = test_kit_with_box
        item_data = {
            "item_type": "tool",
            "item_id": 1
        }

        response = client.post(f"/api/kits/{kit.id}/items",
                             json=item_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_add_item_missing_item_type(self, client, auth_headers_materials, test_kit_with_box):
        """Test adding item without item type (should fail)"""
        kit, box = test_kit_with_box
        item_data = {
            "box_id": box.id,
            "item_id": 1
        }

        response = client.post(f"/api/kits/{kit.id}/items",
                             json=item_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_add_item_missing_item_id(self, client, auth_headers_materials, test_kit_with_box):
        """Test adding item without item ID (should fail)"""
        kit, box = test_kit_with_box
        item_data = {
            "box_id": box.id,
            "item_type": "tool"
        }

        response = client.post(f"/api/kits/{kit.id}/items",
                             json=item_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_add_item_invalid_box(self, client, auth_headers_materials, test_kit_with_box):
        """Test adding item to invalid box (should fail)"""
        kit, _ = test_kit_with_box
        item_data = {
            "box_id": 99999,
            "item_type": "tool",
            "item_id": 1,
            "warehouse_id": 1
        }

        response = client.post(f"/api/kits/{kit.id}/items",
                             json=item_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_add_tool_missing_warehouse(self, client, auth_headers_materials, test_kit_with_box):
        """Test adding tool without warehouse ID (should fail)"""
        kit, box = test_kit_with_box
        item_data = {
            "box_id": box.id,
            "item_type": "tool",
            "item_id": 1
            # Missing warehouse_id
        }

        response = client.post(f"/api/kits/{kit.id}/items",
                             json=item_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "warehouse" in data["error"].lower()

    def test_add_chemical_to_kit(self, client, auth_headers_materials, test_kit_with_box,
                                  test_chemical_in_warehouse, test_warehouse_for_kits):
        """Test adding chemical to kit"""
        kit, box = test_kit_with_box
        item_data = {
            "box_id": box.id,
            "item_type": "chemical",
            "item_id": test_chemical_in_warehouse.id,
            "warehouse_id": test_warehouse_for_kits.id,
            "quantity": 50.0,
            "location": "Box 1"
        }

        response = client.post(f"/api/kits/{kit.id}/items",
                             json=item_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["item_type"] == "chemical"

    def test_add_tool_not_found(self, client, auth_headers_materials, test_kit_with_box, test_warehouse_for_kits):
        """Test adding non-existent tool (should fail)"""
        kit, box = test_kit_with_box
        item_data = {
            "box_id": box.id,
            "item_type": "tool",
            "item_id": 99999,
            "warehouse_id": test_warehouse_for_kits.id
        }

        response = client.post(f"/api/kits/{kit.id}/items",
                             json=item_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_add_tool_wrong_warehouse(self, client, auth_headers_materials, test_kit_with_box,
                                       test_tool_in_warehouse, db_session):
        """Test adding tool from wrong warehouse (should fail)"""
        kit, box = test_kit_with_box

        # Create a different warehouse
        other_warehouse = Warehouse(
            name=f"OtherWarehouse-{uuid.uuid4().hex[:6]}",
            address="789 Other St",
            is_active=True
        )
        db_session.add(other_warehouse)
        db_session.commit()

        item_data = {
            "box_id": box.id,
            "item_type": "tool",
            "item_id": test_tool_in_warehouse.id,
            "warehouse_id": other_warehouse.id  # Wrong warehouse
        }

        response = client.post(f"/api/kits/{kit.id}/items",
                             json=item_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "not in the specified warehouse" in data["error"]

    def test_add_tool_inactive_warehouse(self, client, auth_headers_materials, test_kit_with_box,
                                          db_session):
        """Test adding tool from inactive warehouse (should fail)"""
        kit, box = test_kit_with_box

        inactive_warehouse = Warehouse(
            name=f"InactiveWarehouse-{uuid.uuid4().hex[:6]}",
            address="000 Inactive St",
            is_active=False
        )
        db_session.add(inactive_warehouse)
        db_session.flush()

        tool = Tool(
            tool_number=f"T-{uuid.uuid4().hex[:6]}",
            serial_number=f"SN-{uuid.uuid4().hex[:8]}",
            description="Tool in inactive warehouse",
            condition="Good",
            location="Test",
            category="Testing",
            warehouse_id=inactive_warehouse.id,
            status="available"
        )
        db_session.add(tool)
        db_session.commit()

        item_data = {
            "box_id": box.id,
            "item_type": "tool",
            "item_id": tool.id,
            "warehouse_id": inactive_warehouse.id
        }

        response = client.post(f"/api/kits/{kit.id}/items",
                             json=item_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "inactive" in data["error"].lower()

    def test_add_invalid_item_type(self, client, auth_headers_materials, test_kit_with_box):
        """Test adding item with invalid type (should fail)"""
        kit, box = test_kit_with_box
        item_data = {
            "box_id": box.id,
            "item_type": "invalid_type",
            "item_id": 1
        }

        response = client.post(f"/api/kits/{kit.id}/items",
                             json=item_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_update_kit_item(self, client, auth_headers_materials, db_session, test_kit_with_box):
        """Test updating kit item"""
        kit, box = test_kit_with_box

        kit_item = KitItem(
            kit_id=kit.id,
            box_id=box.id,
            item_type="tool",
            item_id=1,
            part_number="T-001",
            description="Test tool",
            quantity=1,
            location="Box 1",
            status="available"
        )
        db_session.add(kit_item)
        db_session.commit()

        update_data = {
            "quantity": 2,
            "location": "Updated location",
            "status": "low_stock"
        }

        response = client.put(f"/api/kits/{kit.id}/items/{kit_item.id}",
                            json=update_data,
                            headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["quantity"] == 2
        assert data["location"] == "Updated location"
        assert data["status"] == "low_stock"

    def test_remove_kit_item(self, client, auth_headers_materials, db_session, test_kit_with_box):
        """Test removing kit item"""
        kit, box = test_kit_with_box

        kit_item = KitItem(
            kit_id=kit.id,
            box_id=box.id,
            item_type="tool",
            item_id=1,
            part_number="T-002",
            description="Tool to remove",
            quantity=1,
            status="available"
        )
        db_session.add(kit_item)
        db_session.commit()
        item_id = kit_item.id

        response = client.delete(f"/api/kits/{kit.id}/items/{kit_item.id}",
                               headers=auth_headers_materials)

        assert response.status_code == 200

        # Verify item was removed
        removed_item = KitItem.query.get(item_id)
        assert removed_item is None

    def test_get_kit_items_with_box_filter(self, client, auth_headers_user, db_session, test_kit_with_box):
        """Test getting kit items filtered by box"""
        kit, box = test_kit_with_box

        response = client.get(f"/api/kits/{kit.id}/items?box_id={box.id}",
                            headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "items" in data
        assert "expendables" in data


# ==================== Kit Expendable Tests ====================

class TestKitExpendableAdditional:
    """Additional tests for kit expendable management"""

    def test_add_expendable_missing_box_id(self, client, auth_headers_materials, test_kit_with_box):
        """Test adding expendable without box ID (should fail)"""
        kit, _ = test_kit_with_box
        exp_data = {
            "part_number": "EXP-001",
            "description": "Test expendable"
        }

        response = client.post(f"/api/kits/{kit.id}/expendables",
                             json=exp_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_add_expendable_missing_part_number(self, client, auth_headers_materials, test_kit_with_box):
        """Test adding expendable without part number (should fail)"""
        kit, box = test_kit_with_box
        exp_data = {
            "box_id": box.id,
            "description": "Test expendable"
        }

        response = client.post(f"/api/kits/{kit.id}/expendables",
                             json=exp_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_add_expendable_missing_description(self, client, auth_headers_materials, test_kit_with_box):
        """Test adding expendable without description (should fail)"""
        kit, box = test_kit_with_box
        exp_data = {
            "box_id": box.id,
            "part_number": "EXP-001"
        }

        response = client.post(f"/api/kits/{kit.id}/expendables",
                             json=exp_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_add_expendable_invalid_box(self, client, auth_headers_materials, test_kit_with_box):
        """Test adding expendable to invalid box (should fail)"""
        kit, _ = test_kit_with_box
        exp_data = {
            "box_id": 99999,
            "part_number": "EXP-001",
            "description": "Test expendable"
        }

        response = client.post(f"/api/kits/{kit.id}/expendables",
                             json=exp_data,
                             headers=auth_headers_materials)

        assert response.status_code == 400

    def test_add_expendable_with_serial_tracking(self, client, auth_headers_materials, test_kit_with_box, db_session):
        """Test adding expendable with serial number tracking"""
        kit, box = test_kit_with_box
        exp_data = {
            "box_id": box.id,
            "part_number": f"EXP-{uuid.uuid4().hex[:6]}",
            "description": "Serial tracked expendable",
            "serial_number": f"SN-{uuid.uuid4().hex[:8]}",
            "tracking_type": "serial",
            "quantity": 1,
            "unit": "ea"
        }

        response = client.post(f"/api/kits/{kit.id}/expendables",
                             json=exp_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["tracking_type"] == "serial"
        assert data["serial_number"] == exp_data["serial_number"]

    def test_add_expendable_with_lot_tracking(self, client, auth_headers_materials, test_kit_with_box):
        """Test adding expendable with lot number tracking"""
        kit, box = test_kit_with_box
        exp_data = {
            "box_id": box.id,
            "part_number": f"EXP-{uuid.uuid4().hex[:6]}",
            "description": "Lot tracked expendable",
            "lot_number": f"LOT-{uuid.uuid4().hex[:8]}",
            "tracking_type": "lot",
            "quantity": 100,
            "unit": "ea"
        }

        response = client.post(f"/api/kits/{kit.id}/expendables",
                             json=exp_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["tracking_type"] == "lot"
        assert data["lot_number"] == exp_data["lot_number"]

    def test_update_kit_expendable(self, client, auth_headers_materials, db_session, test_kit_with_box):
        """Test updating kit expendable"""
        kit, box = test_kit_with_box

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number="EXP-UPD",
            description="Expendable to update",
            quantity=50,
            unit="ea",
            status="available",
            minimum_stock_level=10
        )
        db_session.add(expendable)
        db_session.commit()

        update_data = {
            "quantity": 75,
            "location": "Shelf A",
            "status": "low_stock",
            "minimum_stock_level": 20
        }

        response = client.put(f"/api/kits/{kit.id}/expendables/{expendable.id}",
                            json=update_data,
                            headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["quantity"] == 75
        assert data["location"] == "Shelf A"
        assert data["status"] == "low_stock"
        assert data["minimum_stock_level"] == 20

    def test_remove_kit_expendable(self, client, auth_headers_materials, db_session, test_kit_with_box):
        """Test removing kit expendable"""
        kit, box = test_kit_with_box

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number="EXP-DEL",
            description="Expendable to delete",
            quantity=10,
            unit="ea",
            status="available"
        )
        db_session.add(expendable)
        db_session.commit()
        exp_id = expendable.id

        response = client.delete(f"/api/kits/{kit.id}/expendables/{expendable.id}",
                               headers=auth_headers_materials)

        assert response.status_code == 200

        # Verify expendable was removed
        removed_exp = KitExpendable.query.get(exp_id)
        assert removed_exp is None

    def test_get_kit_expendables_with_pagination(self, client, auth_headers_user, db_session, test_kit_with_box):
        """Test getting kit expendables with pagination"""
        kit, box = test_kit_with_box

        # Create multiple expendables
        for i in range(15):
            exp = KitExpendable(
                kit_id=kit.id,
                box_id=box.id,
                part_number=f"EXP-{i:03d}",
                description=f"Expendable {i}",
                quantity=i * 10,
                unit="ea",
                status="available"
            )
            db_session.add(exp)
        db_session.commit()

        response = client.get(f"/api/kits/{kit.id}/expendables?page=1&per_page=5",
                            headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "expendables" in data
        assert "pagination" in data
        assert len(data["expendables"]) == 5
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["per_page"] == 5
        assert data["pagination"]["total"] >= 15
        assert data["pagination"]["has_next"] is True

    def test_get_kit_expendables_with_status_filter(self, client, auth_headers_user, db_session, test_kit_with_box):
        """Test getting kit expendables with status filter"""
        kit, box = test_kit_with_box

        exp1 = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number="EXP-AVAIL",
            description="Available expendable",
            quantity=100,
            unit="ea",
            status="available"
        )
        exp2 = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number="EXP-LOW",
            description="Low stock expendable",
            quantity=5,
            unit="ea",
            status="low_stock"
        )
        db_session.add(exp1)
        db_session.add(exp2)
        db_session.commit()

        response = client.get(f"/api/kits/{kit.id}/expendables?status=low_stock",
                            headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        for exp in data["expendables"]:
            assert exp["status"] == "low_stock"

    def test_get_kit_expendables_invalid_pagination(self, client, auth_headers_user, test_kit_with_box):
        """Test getting kit expendables with invalid pagination parameters"""
        kit, _ = test_kit_with_box

        # Page < 1
        response = client.get(f"/api/kits/{kit.id}/expendables?page=0",
                            headers=auth_headers_user)
        assert response.status_code == 400

        # per_page > 500
        response = client.get(f"/api/kits/{kit.id}/expendables?per_page=1000",
                            headers=auth_headers_user)
        assert response.status_code == 400


# ==================== Kit Issuance Tests ====================

class TestKitIssuanceAdditional:
    """Additional tests for kit issuance operations"""

    def test_issue_expendable_missing_item_type(self, client, auth_headers_user, test_kit_with_box):
        """Test issuing without item type (should fail)"""
        kit, _ = test_kit_with_box
        issue_data = {
            "item_id": 1,
            "quantity": 5
        }

        response = client.post(f"/api/kits/{kit.id}/issue",
                             json=issue_data,
                             headers=auth_headers_user)

        assert response.status_code == 400

    def test_issue_expendable_missing_quantity(self, client, auth_headers_user, test_kit_with_box):
        """Test issuing without quantity (should fail)"""
        kit, _ = test_kit_with_box
        issue_data = {
            "item_type": "expendable",
            "item_id": 1
        }

        response = client.post(f"/api/kits/{kit.id}/issue",
                             json=issue_data,
                             headers=auth_headers_user)

        assert response.status_code == 400

    def test_issue_from_kit_item_expendable(self, client, auth_headers_user, db_session, test_kit_with_box):
        """Test issuing expendable from KitItem (new storage method)"""
        kit, box = test_kit_with_box

        # Create expendable as KitItem
        kit_item = KitItem(
            kit_id=kit.id,
            box_id=box.id,
            item_type="expendable",
            item_id=100,
            part_number="EXP-KI",
            description="KitItem expendable",
            quantity=50,
            status="available"
        )
        db_session.add(kit_item)
        db_session.commit()

        issue_data = {
            "item_type": "expendable",
            "item_id": kit_item.id,
            "quantity": 20,
            "purpose": "Testing",
            "work_order": "WO-TEST"
        }

        response = client.post(f"/api/kits/{kit.id}/issue",
                             json=issue_data,
                             headers=auth_headers_user)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["quantity"] == 20

        # Verify quantity was reduced
        db_session.refresh(kit_item)
        assert kit_item.quantity == 30

    def test_issue_triggers_automatic_reorder(self, client, auth_headers_user, db_session, test_kit_with_box):
        """Test that issuing to low stock triggers automatic reorder"""
        kit, box = test_kit_with_box

        # Create expendable at low stock level
        kit_item = KitItem(
            kit_id=kit.id,
            box_id=box.id,
            item_type="expendable",
            item_id=101,
            part_number="EXP-REORDER",
            description="Low stock expendable",
            quantity=15,  # Will drop to 5, triggering reorder (default threshold is 10)
            status="available"
        )
        db_session.add(kit_item)
        db_session.commit()

        issue_data = {
            "item_type": "expendable",
            "item_id": kit_item.id,
            "quantity": 10,
            "purpose": "Causing reorder"
        }

        response = client.post(f"/api/kits/{kit.id}/issue",
                             json=issue_data,
                             headers=auth_headers_user)

        assert response.status_code == 201

        # Verify reorder request was created
        reorder = KitReorderRequest.query.filter_by(
            kit_id=kit.id,
            item_id=kit_item.id,
            status="pending"
        ).first()
        assert reorder is not None
        assert reorder.is_automatic is True

    def test_issue_to_zero_creates_high_priority_reorder(self, client, auth_headers_user, db_session, test_kit_with_box):
        """Test that depleting stock creates high priority reorder"""
        kit, box = test_kit_with_box

        kit_item = KitItem(
            kit_id=kit.id,
            box_id=box.id,
            item_type="expendable",
            item_id=102,
            part_number="EXP-DEPLETE",
            description="To be depleted",
            quantity=5,
            status="available"
        )
        db_session.add(kit_item)
        db_session.commit()

        issue_data = {
            "item_type": "expendable",
            "item_id": kit_item.id,
            "quantity": 5,
            "purpose": "Deplete stock"
        }

        response = client.post(f"/api/kits/{kit.id}/issue",
                             json=issue_data,
                             headers=auth_headers_user)

        assert response.status_code == 201

        # Verify high priority reorder was created
        reorder = KitReorderRequest.query.filter_by(
            kit_id=kit.id,
            item_id=kit_item.id
        ).first()
        assert reorder is not None
        assert reorder.priority == "high"

    def test_issue_expendable_not_found(self, client, auth_headers_user, test_kit_with_box):
        """Test issuing non-existent expendable (should fail)"""
        kit, _ = test_kit_with_box
        issue_data = {
            "item_type": "expendable",
            "item_id": 99999,
            "quantity": 5
        }

        response = client.post(f"/api/kits/{kit.id}/issue",
                             json=issue_data,
                             headers=auth_headers_user)

        assert response.status_code == 400

    def test_get_all_kit_issuances(self, client, auth_headers_user, db_session, test_kit_with_box, materials_user):
        """Test getting all kit issuances across kits"""
        kit, _ = test_kit_with_box

        # Create some issuances
        for i in range(3):
            issuance = KitIssuance(
                kit_id=kit.id,
                item_type="expendable",
                item_id=i + 1,
                issued_by=materials_user.id,
                quantity=i + 1,
                purpose=f"Test purpose {i}"
            )
            db_session.add(issuance)
        db_session.commit()

        response = client.get("/api/kits/issuances", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 3

        # Verify kit_name is included
        for issuance in data:
            assert "kit_name" in issuance

    def test_get_all_kit_issuances_with_filters(self, client, auth_headers_user, db_session,
                                                 test_kit_with_box, materials_user, aircraft_type):
        """Test getting all kit issuances with filters"""
        kit, _ = test_kit_with_box

        issuance = KitIssuance(
            kit_id=kit.id,
            item_type="expendable",
            item_id=1,
            issued_by=materials_user.id,
            quantity=5,
            purpose="Filtered test"
        )
        db_session.add(issuance)
        db_session.commit()

        # Filter by kit_id
        response = client.get(f"/api/kits/issuances?kit_id={kit.id}", headers=auth_headers_user)
        assert response.status_code == 200

        # Filter by aircraft_type_id
        response = client.get(f"/api/kits/issuances?aircraft_type_id={aircraft_type.id}",
                            headers=auth_headers_user)
        assert response.status_code == 200

    def test_get_kit_issuances_with_date_filter(self, client, auth_headers_user, db_session,
                                                 test_kit_with_box, materials_user):
        """Test getting kit issuances with date filter"""
        kit, _ = test_kit_with_box

        issuance = KitIssuance(
            kit_id=kit.id,
            item_type="expendable",
            item_id=1,
            issued_by=materials_user.id,
            quantity=5,
            purpose="Date filter test"
        )
        db_session.add(issuance)
        db_session.commit()

        today = datetime.now().strftime("%Y-%m-%d")
        response = client.get(f"/api/kits/{kit.id}/issuances?start_date={today}",
                            headers=auth_headers_user)

        assert response.status_code == 200


# ==================== Analytics & Reporting Tests ====================

class TestKitAnalyticsAdditional:
    """Additional tests for kit analytics and reporting"""

    def test_get_kit_analytics_with_custom_days(self, client, auth_headers_user, test_kit_with_box):
        """Test getting kit analytics with custom day range"""
        kit, _ = test_kit_with_box

        response = client.get(f"/api/kits/{kit.id}/analytics?days=90",
                            headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["period_days"] == 90

    def test_get_inventory_report_with_kit_filter(self, client, auth_headers_user, test_kit_with_box):
        """Test getting inventory report filtered by specific kit"""
        kit, _ = test_kit_with_box

        response = client.get(f"/api/kits/reports/inventory?kit_id={kit.id}",
                            headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        # Should only return the specified kit
        for item in data:
            assert item["kit_id"] == kit.id

    def test_get_reorder_report(self, client, auth_headers_user, db_session, test_kit_with_box, materials_user):
        """Test getting reorder report"""
        kit, _ = test_kit_with_box

        reorder = KitReorderRequest(
            kit_id=kit.id,
            item_type="expendable",
            item_id=1,
            part_number="REORDER-001",
            description="Reorder test",
            quantity_requested=50,
            priority="high",
            requested_by=materials_user.id,
            status="pending"
        )
        db_session.add(reorder)
        db_session.commit()

        response = client.get("/api/kits/reorders", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1
        # Verify kit_name and requested_by_name are included
        for item in data:
            assert "kit_name" in item
            assert "requested_by_name" in item

    def test_get_reorder_report_with_filters(self, client, auth_headers_user, db_session,
                                              test_kit_with_box, materials_user, aircraft_type):
        """Test getting reorder report with various filters"""
        kit, _ = test_kit_with_box

        reorder = KitReorderRequest(
            kit_id=kit.id,
            item_type="expendable",
            item_id=1,
            part_number="REORDER-FLT",
            description="Filtered reorder",
            quantity_requested=25,
            priority="medium",
            requested_by=materials_user.id,
            status="pending"
        )
        db_session.add(reorder)
        db_session.commit()

        # Filter by status
        response = client.get("/api/kits/reorders?status=pending", headers=auth_headers_user)
        assert response.status_code == 200

        # Filter by kit_id
        response = client.get(f"/api/kits/reorders?kit_id={kit.id}", headers=auth_headers_user)
        assert response.status_code == 200

        # Filter by aircraft_type_id
        response = client.get(f"/api/kits/reorders?aircraft_type_id={aircraft_type.id}",
                            headers=auth_headers_user)
        assert response.status_code == 200

    def test_get_kit_utilization_analytics(self, client, auth_headers_user, db_session,
                                            test_kit_with_box, materials_user):
        """Test getting kit utilization analytics"""
        kit, _ = test_kit_with_box

        # Create some activity data
        issuance = KitIssuance(
            kit_id=kit.id,
            item_type="expendable",
            item_id=1,
            issued_by=materials_user.id,
            quantity=10,
            purpose="Analytics test"
        )
        db_session.add(issuance)
        db_session.commit()

        response = client.get("/api/kits/analytics/utilization", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "issuancesByKit" in data
        assert "transfersByType" in data
        assert "activityOverTime" in data
        assert "summary" in data
        assert "totalIssuances" in data["summary"]
        assert "totalTransfers" in data["summary"]
        assert "activeKits" in data["summary"]
        assert "avgUtilization" in data["summary"]

    def test_get_kit_utilization_analytics_with_filters(self, client, auth_headers_user,
                                                         test_kit_with_box, aircraft_type):
        """Test getting kit utilization analytics with filters"""
        kit, _ = test_kit_with_box

        # Filter by aircraft_type_id
        response = client.get(f"/api/kits/analytics/utilization?aircraft_type_id={aircraft_type.id}",
                            headers=auth_headers_user)
        assert response.status_code == 200

        # Filter by kit_id
        response = client.get(f"/api/kits/analytics/utilization?kit_id={kit.id}",
                            headers=auth_headers_user)
        assert response.status_code == 200

        # Custom days
        response = client.get("/api/kits/analytics/utilization?days=60", headers=auth_headers_user)
        assert response.status_code == 200


# ==================== Kit Alerts Tests ====================

class TestKitAlertsAdditional:
    """Additional tests for kit alerts"""

    def test_get_kit_alerts_low_stock(self, client, auth_headers_user, db_session, test_kit_with_box):
        """Test getting alerts for low stock items"""
        kit, box = test_kit_with_box

        # Create low stock expendable
        exp = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number="LOW-STOCK",
            description="Low stock item",
            quantity=2,
            unit="ea",
            status="available",
            minimum_stock_level=10
        )
        db_session.add(exp)
        db_session.commit()

        response = client.get(f"/api/kits/{kit.id}/alerts", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "alerts" in data
        # Should have at least one low stock alert
        low_stock_alerts = [a for a in data["alerts"] if a["type"] == "low_stock"]
        assert len(low_stock_alerts) >= 1

    def test_get_kit_alerts_pending_reorders(self, client, auth_headers_user, db_session,
                                              test_kit_with_box, materials_user):
        """Test getting alerts for pending reorders"""
        kit, _ = test_kit_with_box

        reorder = KitReorderRequest(
            kit_id=kit.id,
            item_type="expendable",
            item_id=1,
            part_number="ALERT-REORDER",
            description="Alert reorder",
            quantity_requested=50,
            priority="high",
            requested_by=materials_user.id,
            status="pending"
        )
        db_session.add(reorder)
        db_session.commit()

        response = client.get(f"/api/kits/{kit.id}/alerts", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        pending_reorder_alerts = [a for a in data["alerts"] if a["type"] == "pending_reorders"]
        assert len(pending_reorder_alerts) >= 1

    def test_get_kit_alerts_unread_messages(self, client, auth_headers_user, db_session,
                                             test_kit_with_box, materials_user, regular_user):
        """Test getting alerts for unread messages"""
        kit, _ = test_kit_with_box

        message = KitMessage(
            kit_id=kit.id,
            sender_id=materials_user.id,
            recipient_id=regular_user.id,
            subject="Test Alert Subject",
            message="Unread message",
            is_read=False
        )
        db_session.add(message)
        db_session.commit()

        response = client.get(f"/api/kits/{kit.id}/alerts", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        # Check for unread message alerts
        assert "alerts" in data


# ==================== Recent Activity Tests ====================

class TestRecentActivityAdditional:
    """Tests for recent kit activity endpoint"""

    def test_get_recent_activity(self, client, auth_headers_user):
        """Test getting recent kit activity"""
        response = client.get("/api/kits/recent-activity", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_recent_activity_with_limit(self, client, auth_headers_user):
        """Test getting recent activity with custom limit"""
        response = client.get("/api/kits/recent-activity?limit=5", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) <= 5

    def test_get_recent_activity_with_high_limit(self, client, auth_headers_user):
        """Test that limit is capped at 50"""
        response = client.get("/api/kits/recent-activity?limit=100", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) <= 50

    def test_get_recent_activity_includes_issuances(self, client, auth_headers_user, db_session,
                                                     test_kit_with_box, materials_user):
        """Test that recent activity includes issuances"""
        kit, _ = test_kit_with_box

        issuance = KitIssuance(
            kit_id=kit.id,
            item_type="expendable",
            item_id=1,
            issued_by=materials_user.id,
            quantity=5,
            purpose="Recent activity test"
        )
        db_session.add(issuance)
        db_session.commit()

        response = client.get("/api/kits/recent-activity", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        issuance_activities = [a for a in data if a["type"] == "issuance"]
        assert len(issuance_activities) >= 1

    def test_get_recent_activity_includes_transfers(self, client, auth_headers_user, db_session,
                                                     test_kit_with_box, materials_user):
        """Test that recent activity includes transfers"""
        kit, _ = test_kit_with_box

        transfer = KitTransfer(
            from_location_type="kit",
            from_location_id=kit.id,
            to_location_type="warehouse",
            to_location_id=1,
            item_type="expendable",
            item_id=1,
            quantity=10,
            transferred_by=materials_user.id,
            status="completed"
        )
        db_session.add(transfer)
        db_session.commit()

        response = client.get("/api/kits/recent-activity", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        transfer_activities = [a for a in data if a["type"] == "transfer"]
        assert len(transfer_activities) >= 1

    def test_get_recent_activity_includes_reorders(self, client, auth_headers_user, db_session,
                                                    test_kit_with_box, materials_user):
        """Test that recent activity includes reorder requests"""
        kit, _ = test_kit_with_box

        reorder = KitReorderRequest(
            kit_id=kit.id,
            item_type="expendable",
            item_id=1,
            part_number="ACT-REORDER",
            description="Activity reorder",
            quantity_requested=25,
            priority="medium",
            requested_by=materials_user.id,
            status="pending"
        )
        db_session.add(reorder)
        db_session.commit()

        response = client.get("/api/kits/recent-activity", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        reorder_activities = [a for a in data if a["type"] == "reorder"]
        assert len(reorder_activities) >= 1

    def test_recent_activity_sorted_by_timestamp(self, client, auth_headers_user, db_session,
                                                  test_kit_with_box, materials_user):
        """Test that recent activities are sorted by timestamp (most recent first)"""
        kit, _ = test_kit_with_box

        # Create activities at different times
        for i in range(3):
            issuance = KitIssuance(
                kit_id=kit.id,
                item_type="expendable",
                item_id=i + 1,
                issued_by=materials_user.id,
                quantity=i + 1,
                purpose=f"Sort test {i}"
            )
            db_session.add(issuance)
        db_session.commit()

        response = client.get("/api/kits/recent-activity", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        # Verify activities are sorted by timestamp (descending)
        timestamps = [a.get("timestamp") for a in data if a.get("timestamp")]
        if len(timestamps) > 1:
            for i in range(len(timestamps) - 1):
                assert timestamps[i] >= timestamps[i + 1]
