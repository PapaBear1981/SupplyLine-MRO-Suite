"""
Tests for History Routes

This module tests the history tracking endpoints including:
- Item history lookup by identifier and tracking number
- Tool, Chemical, and KitExpendable history tracking
- Parent/child lot relationships
- Transfer history (warehouse and kit)
- Checkout, issuance, and return history
- Audit log tracking for status changes
- Case-insensitive searches
"""

import json
from datetime import datetime, timedelta

import pytest

from models import (
    AuditLog,
    Chemical,
    ChemicalIssuance,
    ChemicalReturn,
    Checkout,
    InventoryTransaction,
    Tool,
    User,
    Warehouse,
    WarehouseTransfer,
    db,
)
from models_kits import (
    AircraftType,
    Kit,
    KitBox,
    KitExpendable,
    KitIssuance,
    KitItem,
    KitTransfer,
)


@pytest.fixture
def test_warehouse(db_session):
    """Create a test warehouse"""
    warehouse = Warehouse(
        name="Test Warehouse",
        warehouse_type="main",
        is_active=True,
    )
    db_session.add(warehouse)
    db_session.commit()
    return warehouse


@pytest.fixture
def test_warehouse_2(db_session):
    """Create a second test warehouse"""
    warehouse = Warehouse(
        name="Secondary Warehouse",
        warehouse_type="satellite",
        is_active=True,
    )
    db_session.add(warehouse)
    db_session.commit()
    return warehouse


@pytest.fixture
def aircraft_type(db_session):
    """Create a test aircraft type"""
    aircraft = AircraftType(
        name="Q400",
        description="Bombardier Q400",
        is_active=True,
    )
    db_session.add(aircraft)
    db_session.commit()
    return aircraft


@pytest.fixture
def test_kit(db_session, aircraft_type, admin_user):
    """Create a test kit"""
    kit = Kit(
        name="Q400-001",
        aircraft_type_id=aircraft_type.id,
        description="Test Kit",
        status="active",
        created_by=admin_user.id,
    )
    db_session.add(kit)
    db_session.commit()
    return kit


@pytest.fixture
def test_kit_2(db_session, aircraft_type, admin_user):
    """Create a second test kit"""
    kit = Kit(
        name="Q400-002",
        aircraft_type_id=aircraft_type.id,
        description="Second Test Kit",
        status="active",
        created_by=admin_user.id,
    )
    db_session.add(kit)
    db_session.commit()
    return kit


@pytest.fixture
def test_kit_box(db_session, test_kit):
    """Create a test kit box"""
    box = KitBox(
        kit_id=test_kit.id,
        box_number="Box1",
        box_type="expendable",
        description="Test Box",
    )
    db_session.add(box)
    db_session.commit()
    return box


@pytest.fixture
def test_user(db_session):
    """Create a test user for history tracking"""
    from werkzeug.security import generate_password_hash

    user = User(
        name="History User",
        employee_number="HIST001",
        department="Maintenance",
        password_hash=generate_password_hash("test123"),
        is_admin=False,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def tool_with_warehouse(db_session, test_warehouse):
    """Create a tool in a warehouse"""
    tool = Tool(
        tool_number="T-12345",
        serial_number="SN-001",
        lot_number="LOT-001",
        description="Test Wrench",
        condition="Good",
        location="Shelf A1",
        category="Hand Tools",
        status="available",
        warehouse_id=test_warehouse.id,
        requires_calibration=True,
        calibration_status="calibrated",
        last_calibration_date=datetime.utcnow() - timedelta(days=30),
        next_calibration_date=datetime.utcnow() + timedelta(days=335),
    )
    db_session.add(tool)
    db_session.commit()
    return tool


@pytest.fixture
def tool_without_warehouse(db_session):
    """Create a tool without warehouse assignment"""
    tool = Tool(
        tool_number="T-99999",
        serial_number="SN-999",
        description="Orphan Tool",
        condition="Fair",
        location="Unknown Location",
        category="Testing",
        status="available",
    )
    db_session.add(tool)
    db_session.commit()
    return tool


@pytest.fixture
def tool_in_kit(db_session, test_kit, test_kit_box):
    """Create a tool that is in a kit"""
    tool = Tool(
        tool_number="T-KIT-001",
        serial_number="SN-KIT-001",
        description="Kit Tool",
        condition="Good",
        location="Kit Box",
        category="Tooling",
        status="available",
        warehouse_id=None,
    )
    db_session.add(tool)
    db_session.flush()

    kit_item = KitItem(
        kit_id=test_kit.id,
        box_id=test_kit_box.id,
        item_type="tool",
        item_id=tool.id,
        part_number=tool.tool_number,
        serial_number=tool.serial_number,
        description=tool.description,
        quantity=1.0,
        location="Position A",
        status="available",
    )
    db_session.add(kit_item)
    db_session.commit()
    return tool


@pytest.fixture
def chemical_with_warehouse(db_session, test_warehouse):
    """Create a chemical in a warehouse"""
    chemical = Chemical(
        part_number="CHEM-001",
        lot_number="LOT-251014-0001",
        description="Industrial Adhesive",
        manufacturer="ChemCorp",
        quantity=100,
        unit="ml",
        location="Cabinet B2",
        category="Adhesive",
        status="available",
        warehouse_id=test_warehouse.id,
        expiration_date=datetime.utcnow() + timedelta(days=365),
    )
    db_session.add(chemical)
    db_session.commit()
    return chemical


@pytest.fixture
def chemical_with_parent(db_session, test_warehouse):
    """Create a chemical with parent lot"""
    # Parent chemical
    parent = Chemical(
        part_number="CHEM-002",
        lot_number="PARENT-LOT",
        description="Sealant",
        manufacturer="SealMaster",
        quantity=500,
        unit="oz",
        location="Storage A",
        category="Sealant",
        status="available",
        warehouse_id=test_warehouse.id,
    )
    db_session.add(parent)
    db_session.flush()

    # Child chemical
    child = Chemical(
        part_number="CHEM-002",
        lot_number="CHILD-LOT",
        description="Sealant",
        manufacturer="SealMaster",
        quantity=100,
        unit="oz",
        location="Storage B",
        category="Sealant",
        status="available",
        warehouse_id=test_warehouse.id,
        parent_lot_number="PARENT-LOT",
        lot_sequence=1,
    )
    db_session.add(child)
    db_session.commit()
    return child


@pytest.fixture
def chemical_without_warehouse(db_session):
    """Create a chemical without warehouse assignment"""
    chemical = Chemical(
        part_number="CHEM-ORPHAN",
        lot_number="LOT-ORPHAN",
        description="Orphan Chemical",
        manufacturer="Unknown",
        quantity=10,
        unit="each",
        location="Unknown",
        category="General",
        status="available",
        warehouse_id=None,
    )
    db_session.add(chemical)
    db_session.commit()
    return chemical


@pytest.fixture
def chemical_in_kit(db_session, test_kit, test_kit_box):
    """Create a chemical that is in a kit"""
    chemical = Chemical(
        part_number="CHEM-KIT",
        lot_number="LOT-KIT",
        description="Kit Chemical",
        manufacturer="KitChem",
        quantity=50,
        unit="ml",
        category="Solvent",
        status="available",
        warehouse_id=None,
    )
    db_session.add(chemical)
    db_session.flush()

    kit_item = KitItem(
        kit_id=test_kit.id,
        box_id=test_kit_box.id,
        item_type="chemical",
        item_id=chemical.id,
        part_number=chemical.part_number,
        lot_number=chemical.lot_number,
        description=chemical.description,
        quantity=50.0,
        location="Compartment C",
        status="available",
    )
    db_session.add(kit_item)
    db_session.commit()
    return chemical


@pytest.fixture
def kit_expendable(db_session, test_kit, test_kit_box):
    """Create a kit expendable"""
    expendable = KitExpendable(
        kit_id=test_kit.id,
        box_id=test_kit_box.id,
        part_number="EXP-001",
        serial_number="SN-EXP-001",
        lot_number=None,
        tracking_type="serial",
        description="Expendable Item",
        quantity=10.0,
        unit="each",
        status="available",
        location="Bin D1",
    )
    db_session.add(expendable)
    db_session.commit()
    return expendable


@pytest.fixture
def kit_expendable_lot(db_session, test_kit, test_kit_box):
    """Create a kit expendable tracked by lot"""
    expendable = KitExpendable(
        kit_id=test_kit.id,
        box_id=test_kit_box.id,
        part_number="EXP-002",
        serial_number=None,
        lot_number="LOT-EXP-002",
        tracking_type="lot",
        description="Lot Tracked Expendable",
        quantity=25.0,
        unit="oz",
        status="available",
        location="Bin D2",
    )
    db_session.add(expendable)
    db_session.commit()
    return expendable


class TestHistoryLookupAuthentication:
    """Test authentication requirements for history lookup"""

    def test_lookup_without_token(self, client, db_session):
        """Test that lookup requires authentication"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
        )
        assert response.status_code == 401

    def test_lookup_with_invalid_token(self, client, db_session):
        """Test that invalid token is rejected"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401


class TestHistoryLookupValidation:
    """Test input validation for history lookup"""

    def test_missing_identifier(self, client, auth_headers_user, db_session):
        """Test that identifier is required"""
        response = client.post(
            "/api/history/lookup",
            json={"tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "identifier" in data["error"].lower() or "Both" in data["error"]

    def test_missing_tracking_number(self, client, auth_headers_user, db_session):
        """Test that tracking_number is required"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345"},
            headers=auth_headers_user,
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "tracking_number" in data["error"].lower() or "Both" in data["error"]

    def test_empty_request_body(self, client, auth_headers_user, db_session):
        """Test empty request body"""
        response = client.post(
            "/api/history/lookup", json={}, headers=auth_headers_user
        )
        assert response.status_code == 400

    def test_no_request_body(self, client, auth_headers_user, db_session):
        """Test request without JSON body returns error"""
        response = client.post(
            "/api/history/lookup",
            headers=auth_headers_user,
            content_type="application/json",
        )
        # Server returns 500 because get_json() raises BadRequest without silent=True
        assert response.status_code in (400, 500)


class TestHistoryLookupNotFound:
    """Test history lookup when item is not found"""

    def test_item_not_found(self, client, auth_headers_user, db_session):
        """Test lookup for non-existent item"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "NONEXISTENT", "tracking_number": "NOTFOUND"},
            headers=auth_headers_user,
        )
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["item_found"] is False
        assert "NONEXISTENT" in data["message"]
        assert "NOTFOUND" in data["message"]


class TestToolHistoryLookup:
    """Test tool history lookup functionality"""

    def test_tool_lookup_by_serial_number(
        self, client, auth_headers_user, db_session, tool_with_warehouse
    ):
        """Test looking up tool by serial number"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["item_found"] is True
        assert data["item_type"] == "tool"
        assert data["item_details"]["tool_number"] == "T-12345"
        assert data["item_details"]["serial_number"] == "SN-001"
        assert data["item_details"]["lot_number"] == "LOT-001"
        assert data["item_details"]["condition"] == "Good"
        assert data["item_details"]["status"] == "available"
        assert data["item_details"]["warehouse_name"] == "Test Warehouse"
        assert data["item_details"]["requires_calibration"] is True
        assert data["item_details"]["calibration_status"] == "calibrated"
        assert data["current_location"]["type"] == "warehouse"
        assert data["current_location"]["name"] == "Test Warehouse"

    def test_tool_lookup_by_lot_number(
        self, client, auth_headers_user, db_session, tool_with_warehouse
    ):
        """Test looking up tool by lot number"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "LOT-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["item_found"] is True
        assert data["item_type"] == "tool"
        assert data["item_details"]["lot_number"] == "LOT-001"

    def test_tool_case_insensitive_lookup(
        self, client, auth_headers_user, db_session, tool_with_warehouse
    ):
        """Test case-insensitive tool lookup"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "t-12345", "tracking_number": "sn-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["item_found"] is True
        assert data["item_type"] == "tool"

    def test_tool_in_kit_location(
        self, client, auth_headers_user, db_session, tool_in_kit, test_kit
    ):
        """Test tool that is currently in a kit"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-KIT-001", "tracking_number": "SN-KIT-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["item_found"] is True
        assert data["current_location"]["type"] == "kit"
        assert data["current_location"]["name"] == "Q400-001"
        assert data["current_location"]["details"] == "Position A"

    def test_tool_unknown_location(
        self, client, auth_headers_user, db_session, tool_without_warehouse
    ):
        """Test tool with unknown location"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-99999", "tracking_number": "SN-999"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["item_found"] is True
        assert data["current_location"]["type"] == "unknown"
        assert data["current_location"]["name"] == "Unknown Location"

    def test_tool_creation_history(
        self, client, auth_headers_user, db_session, tool_with_warehouse
    ):
        """Test that creation event is in history"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        history = data["history"]
        creation_events = [e for e in history if e["event_type"] == "creation"]
        assert len(creation_events) == 1
        assert "Tool added to inventory" in creation_events[0]["description"]


class TestChemicalHistoryLookup:
    """Test chemical history lookup functionality"""

    def test_chemical_lookup_basic(
        self, client, auth_headers_user, db_session, chemical_with_warehouse
    ):
        """Test basic chemical lookup"""
        response = client.post(
            "/api/history/lookup",
            json={
                "identifier": "CHEM-001",
                "tracking_number": "LOT-251014-0001",
            },
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["item_found"] is True
        assert data["item_type"] == "chemical"
        assert data["item_details"]["part_number"] == "CHEM-001"
        assert data["item_details"]["lot_number"] == "LOT-251014-0001"
        assert data["item_details"]["manufacturer"] == "ChemCorp"
        assert data["item_details"]["quantity"] == 100
        assert data["item_details"]["unit"] == "ml"
        assert data["item_details"]["warehouse_name"] == "Test Warehouse"
        assert data["current_location"]["type"] == "warehouse"

    def test_chemical_case_insensitive_lookup(
        self, client, auth_headers_user, db_session, chemical_with_warehouse
    ):
        """Test case-insensitive chemical lookup"""
        response = client.post(
            "/api/history/lookup",
            json={
                "identifier": "chem-001",
                "tracking_number": "lot-251014-0001",
            },
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["item_found"] is True
        assert data["item_type"] == "chemical"

    def test_chemical_with_parent_lot(
        self, client, auth_headers_user, db_session, chemical_with_parent, test_warehouse
    ):
        """Test chemical with parent lot information"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "CHEM-002", "tracking_number": "CHILD-LOT"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["item_found"] is True
        assert data["parent_lot"] is not None
        assert data["parent_lot"]["lot_number"] == "PARENT-LOT"
        assert data["parent_lot"]["quantity"] == 500

    def test_chemical_with_child_lots(
        self, client, auth_headers_user, db_session, chemical_with_parent, test_warehouse
    ):
        """Test chemical that has child lots"""
        # Lookup the parent lot
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "CHEM-002", "tracking_number": "PARENT-LOT"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["item_found"] is True
        assert len(data["child_lots"]) == 1
        assert data["child_lots"][0]["lot_number"] == "CHILD-LOT"
        assert data["child_lots"][0]["quantity"] == 100

    def test_chemical_in_kit_location(
        self, client, auth_headers_user, db_session, chemical_in_kit, test_kit
    ):
        """Test chemical that is currently in a kit"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "CHEM-KIT", "tracking_number": "LOT-KIT"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["item_found"] is True
        assert data["current_location"]["type"] == "kit"
        assert data["current_location"]["name"] == "Q400-001"
        assert data["current_location"]["details"] == "Compartment C"

    def test_chemical_unknown_location(
        self, client, auth_headers_user, db_session, chemical_without_warehouse
    ):
        """Test chemical with unknown location"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "CHEM-ORPHAN", "tracking_number": "LOT-ORPHAN"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["item_found"] is True
        assert data["current_location"]["type"] == "unknown"

    def test_chemical_creation_history(
        self, client, auth_headers_user, db_session, chemical_with_warehouse
    ):
        """Test that creation event is in history"""
        response = client.post(
            "/api/history/lookup",
            json={
                "identifier": "CHEM-001",
                "tracking_number": "LOT-251014-0001",
            },
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        history = data["history"]
        creation_events = [e for e in history if e["event_type"] == "creation"]
        assert len(creation_events) == 1
        assert "Chemical added to inventory" in creation_events[0]["description"]


class TestKitExpendableHistoryLookup:
    """Test kit expendable history lookup functionality"""

    def test_expendable_lookup_by_serial_number(
        self, client, auth_headers_user, db_session, kit_expendable, test_kit
    ):
        """Test looking up expendable by serial number"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "EXP-001", "tracking_number": "SN-EXP-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["item_found"] is True
        assert data["item_type"] == "expendable"
        assert data["item_details"]["part_number"] == "EXP-001"
        assert data["item_details"]["serial_number"] == "SN-EXP-001"
        assert data["item_details"]["quantity"] == 10.0
        assert data["item_details"]["unit"] == "each"
        assert data["item_details"]["kit_name"] == "Q400-001"
        assert data["current_location"]["type"] == "kit"
        assert data["current_location"]["name"] == "Q400-001"

    def test_expendable_lookup_by_lot_number(
        self, client, auth_headers_user, db_session, kit_expendable_lot, test_kit
    ):
        """Test looking up expendable by lot number"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "EXP-002", "tracking_number": "LOT-EXP-002"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["item_found"] is True
        assert data["item_type"] == "expendable"
        assert data["item_details"]["lot_number"] == "LOT-EXP-002"

    def test_expendable_case_insensitive_lookup(
        self, client, auth_headers_user, db_session, kit_expendable
    ):
        """Test case-insensitive expendable lookup"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "exp-001", "tracking_number": "sn-exp-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["item_found"] is True
        assert data["item_type"] == "expendable"

    def test_expendable_creation_history(
        self, client, auth_headers_user, db_session, kit_expendable
    ):
        """Test that creation event is in history"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "EXP-001", "tracking_number": "SN-EXP-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        history = data["history"]
        creation_events = [e for e in history if e["event_type"] == "creation"]
        assert len(creation_events) == 1
        assert "Expendable added to kit" in creation_events[0]["description"]


class TestToolHistoryEvents:
    """Test tool history event tracking"""

    def test_tool_checkout_history(
        self, client, auth_headers_user, db_session, tool_with_warehouse, test_user
    ):
        """Test tool checkout appears in history"""
        checkout = Checkout(
            tool_id=tool_with_warehouse.id,
            user_id=test_user.id,
            checkout_date=datetime.utcnow() - timedelta(hours=5),
            expected_return_date=datetime.utcnow() + timedelta(days=1),
        )
        db_session.add(checkout)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        checkout_events = [
            e for e in data["history"] if e["event_type"] == "checkout"
        ]
        assert len(checkout_events) == 1
        assert "Checked out to" in checkout_events[0]["description"]
        assert "History User" in checkout_events[0]["description"]

    def test_tool_return_history(
        self, client, auth_headers_user, db_session, tool_with_warehouse, test_user
    ):
        """Test tool return appears in history"""
        checkout = Checkout(
            tool_id=tool_with_warehouse.id,
            user_id=test_user.id,
            checkout_date=datetime.utcnow() - timedelta(hours=5),
            return_date=datetime.utcnow(),
            expected_return_date=datetime.utcnow() + timedelta(days=1),
        )
        db_session.add(checkout)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        return_events = [e for e in data["history"] if e["event_type"] == "return"]
        assert len(return_events) == 1
        assert "Returned by" in return_events[0]["description"]

    def test_tool_audit_log_retirement(
        self, client, auth_headers_user, db_session, tool_with_warehouse
    ):
        """Test tool retirement audit log appears in history"""
        audit_log = AuditLog(
            action_type="tool_retired",
            action_details=f"Tool T-12345 SN-001 retired due to damage",
            timestamp=datetime.utcnow(),
        )
        db_session.add(audit_log)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        retirement_events = [
            e for e in data["history"] if e["event_type"] == "retirement"
        ]
        assert len(retirement_events) == 1
        assert "retired" in retirement_events[0]["description"].lower()

    def test_tool_audit_log_status_change(
        self, client, auth_headers_user, db_session, tool_with_warehouse
    ):
        """Test tool status change audit log appears in history"""
        audit_log = AuditLog(
            action_type="tool_status_changed",
            action_details=f"Tool T-12345 SN-001 status changed to maintenance",
            timestamp=datetime.utcnow(),
        )
        db_session.add(audit_log)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        status_events = [
            e for e in data["history"] if e["event_type"] == "status_change"
        ]
        assert len(status_events) == 1
        assert "Status changed" in status_events[0]["description"]

    def test_tool_audit_log_update(
        self, client, auth_headers_user, db_session, tool_with_warehouse
    ):
        """Test tool update audit log appears in history"""
        audit_log = AuditLog(
            action_type="tool_updated",
            action_details=f"Tool T-12345 SN-001 description updated",
            timestamp=datetime.utcnow(),
        )
        db_session.add(audit_log)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        update_events = [e for e in data["history"] if e["event_type"] == "update"]
        assert len(update_events) == 1
        assert "Updated" in update_events[0]["description"]


class TestChemicalHistoryEvents:
    """Test chemical history event tracking"""

    def test_chemical_issuance_history(
        self, client, auth_headers_user, db_session, chemical_with_warehouse, test_user
    ):
        """Test chemical issuance appears in history"""
        issuance = ChemicalIssuance(
            chemical_id=chemical_with_warehouse.id,
            user_id=test_user.id,
            quantity=10,
            hangar="Hangar A",
            purpose="Aircraft maintenance",
            issue_date=datetime.utcnow() - timedelta(hours=2),
        )
        db_session.add(issuance)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={
                "identifier": "CHEM-001",
                "tracking_number": "LOT-251014-0001",
            },
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        issuance_events = [
            e for e in data["history"] if e["event_type"] == "issuance"
        ]
        assert len(issuance_events) == 1
        assert "Issued 10 ml" in issuance_events[0]["description"]
        assert "Hangar A" in issuance_events[0]["description"]

    def test_chemical_return_history(
        self, client, auth_headers_user, db_session, chemical_with_warehouse, test_user, test_warehouse
    ):
        """Test chemical return appears in history"""
        issuance = ChemicalIssuance(
            chemical_id=chemical_with_warehouse.id,
            user_id=test_user.id,
            quantity=10,
            hangar="Hangar B",
            purpose="Testing",
        )
        db_session.add(issuance)
        db_session.flush()

        chem_return = ChemicalReturn(
            chemical_id=chemical_with_warehouse.id,
            issuance_id=issuance.id,
            returned_by_id=test_user.id,
            quantity=5,
            warehouse_id=test_warehouse.id,
            notes="Partially used",
            return_date=datetime.utcnow(),
        )
        db_session.add(chem_return)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={
                "identifier": "CHEM-001",
                "tracking_number": "LOT-251014-0001",
            },
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        return_events = [e for e in data["history"] if e["event_type"] == "return"]
        assert len(return_events) == 1
        assert "Returned 5 ml" in return_events[0]["description"]
        assert "Test Warehouse" in return_events[0]["description"]

    def test_chemical_return_with_location_no_warehouse(
        self, client, auth_headers_user, db_session, chemical_with_warehouse, test_user
    ):
        """Test chemical return to location without warehouse"""
        issuance = ChemicalIssuance(
            chemical_id=chemical_with_warehouse.id,
            user_id=test_user.id,
            quantity=10,
            hangar="Hangar C",
            purpose="Testing",
        )
        db_session.add(issuance)
        db_session.flush()

        chem_return = ChemicalReturn(
            chemical_id=chemical_with_warehouse.id,
            issuance_id=issuance.id,
            returned_by_id=test_user.id,
            quantity=3,
            warehouse_id=None,
            location="Floor Storage",
            notes="Temporary storage",
            return_date=datetime.utcnow(),
        )
        db_session.add(chem_return)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={
                "identifier": "CHEM-001",
                "tracking_number": "LOT-251014-0001",
            },
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        return_events = [e for e in data["history"] if e["event_type"] == "return"]
        assert len(return_events) == 1
        assert "Floor Storage" in return_events[0]["description"]


class TestInventoryTransactionHistory:
    """Test inventory transaction history tracking"""

    def test_receipt_transaction(
        self, client, auth_headers_user, db_session, tool_with_warehouse, test_user
    ):
        """Test receipt transaction appears in history"""
        transaction = InventoryTransaction(
            item_type="tool",
            item_id=tool_with_warehouse.id,
            transaction_type="receipt",
            timestamp=datetime.utcnow(),
            user_id=test_user.id,
            quantity_change=1,
            location_from=None,
            location_to="Shelf A1",
            reference_number="PO-12345",
            notes="New tool received",
        )
        db_session.add(transaction)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        receipt_events = [
            e for e in data["history"] if e["event_type"] == "receipt"
        ]
        assert len(receipt_events) == 1
        assert "Received into inventory" in receipt_events[0]["description"]
        assert receipt_events[0]["details"]["reference_number"] == "PO-12345"

    def test_issuance_transaction(
        self, client, auth_headers_user, db_session, chemical_with_warehouse, test_user
    ):
        """Test issuance transaction appears in history"""
        transaction = InventoryTransaction(
            item_type="chemical",
            item_id=chemical_with_warehouse.id,
            transaction_type="issuance",
            timestamp=datetime.utcnow(),
            user_id=test_user.id,
            quantity_change=-10,
            location_from="Cabinet B2",
            location_to="Hangar A",
            notes="Issued for maintenance",
        )
        db_session.add(transaction)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={
                "identifier": "CHEM-001",
                "tracking_number": "LOT-251014-0001",
            },
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        issuance_events = [
            e for e in data["history"] if e["event_type"] == "issuance"
        ]
        assert len(issuance_events) >= 1
        trans_event = [e for e in issuance_events if "Issued - " in e["description"]]
        assert len(trans_event) == 1

    def test_transfer_transaction(
        self, client, auth_headers_user, db_session, tool_with_warehouse, test_user
    ):
        """Test transfer transaction appears in history"""
        transaction = InventoryTransaction(
            item_type="tool",
            item_id=tool_with_warehouse.id,
            transaction_type="transfer",
            timestamp=datetime.utcnow(),
            user_id=test_user.id,
            quantity_change=0,
            location_from="Shelf A1",
            location_to="Shelf B2",
            notes=None,
        )
        db_session.add(transaction)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        transfer_events = [
            e for e in data["history"] if e["event_type"] == "transfer"
        ]
        assert len(transfer_events) == 1
        assert "Transferred from Shelf A1 to Shelf B2" in transfer_events[0]["description"]

    def test_adjustment_transaction(
        self, client, auth_headers_user, db_session, chemical_with_warehouse, test_user
    ):
        """Test adjustment transaction appears in history"""
        transaction = InventoryTransaction(
            item_type="chemical",
            item_id=chemical_with_warehouse.id,
            transaction_type="adjustment",
            timestamp=datetime.utcnow(),
            user_id=test_user.id,
            quantity_change=-5,
            notes="Inventory count correction",
        )
        db_session.add(transaction)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={
                "identifier": "CHEM-001",
                "tracking_number": "LOT-251014-0001",
            },
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        adjustment_events = [
            e for e in data["history"] if e["event_type"] == "adjustment"
        ]
        assert len(adjustment_events) == 1
        assert "Inventory adjustment" in adjustment_events[0]["description"]

    def test_checkout_transaction(
        self, client, auth_headers_user, db_session, tool_with_warehouse, test_user
    ):
        """Test checkout transaction appears in history"""
        transaction = InventoryTransaction(
            item_type="tool",
            item_id=tool_with_warehouse.id,
            transaction_type="checkout",
            timestamp=datetime.utcnow(),
            user_id=test_user.id,
            notes="Checked out for project",
        )
        db_session.add(transaction)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        checkout_events = [
            e for e in data["history"] if e["event_type"] == "checkout"
        ]
        assert len(checkout_events) >= 1

    def test_return_transaction(
        self, client, auth_headers_user, db_session, tool_with_warehouse, test_user
    ):
        """Test return transaction appears in history"""
        transaction = InventoryTransaction(
            item_type="tool",
            item_id=tool_with_warehouse.id,
            transaction_type="return",
            timestamp=datetime.utcnow(),
            user_id=test_user.id,
            notes=None,
        )
        db_session.add(transaction)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        return_events = [
            e for e in data["history"] if e["event_type"] == "return"
        ]
        assert len(return_events) >= 1

    def test_kit_issuance_transaction(
        self, client, auth_headers_user, db_session, tool_with_warehouse, test_user
    ):
        """Test kit_issuance transaction type"""
        transaction = InventoryTransaction(
            item_type="tool",
            item_id=tool_with_warehouse.id,
            transaction_type="kit_issuance",
            timestamp=datetime.utcnow(),
            user_id=test_user.id,
            notes="Issued from kit",
        )
        db_session.add(transaction)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        kit_issuance_events = [
            e for e in data["history"] if e["event_type"] == "kit_issuance"
        ]
        assert len(kit_issuance_events) == 1
        assert "Issued from kit" in kit_issuance_events[0]["description"]

    def test_unknown_transaction_type(
        self, client, auth_headers_user, db_session, tool_with_warehouse, test_user
    ):
        """Test unknown transaction type formatting"""
        transaction = InventoryTransaction(
            item_type="tool",
            item_id=tool_with_warehouse.id,
            transaction_type="custom_type",
            timestamp=datetime.utcnow(),
            user_id=test_user.id,
            notes="Custom transaction",
        )
        db_session.add(transaction)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        custom_events = [
            e for e in data["history"] if e["event_type"] == "custom_type"
        ]
        assert len(custom_events) == 1
        assert "Custom Type" in custom_events[0]["description"]


class TestWarehouseTransferHistory:
    """Test warehouse transfer history tracking"""

    def test_warehouse_to_warehouse_transfer(
        self,
        client,
        auth_headers_user,
        db_session,
        tool_with_warehouse,
        test_warehouse,
        test_warehouse_2,
        test_user,
    ):
        """Test warehouse to warehouse transfer appears in history"""
        transfer = WarehouseTransfer(
            from_warehouse_id=test_warehouse.id,
            to_warehouse_id=test_warehouse_2.id,
            to_kit_id=None,
            from_kit_id=None,
            item_type="tool",
            item_id=tool_with_warehouse.id,
            quantity=1,
            transfer_date=datetime.utcnow(),
            transferred_by_id=test_user.id,
            notes="Inter-warehouse transfer",
            status="completed",
        )
        db_session.add(transfer)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        transfer_events = [
            e
            for e in data["history"]
            if e["event_type"] == "warehouse_to_warehouse_transfer"
        ]
        assert len(transfer_events) == 1
        assert "Test Warehouse" in transfer_events[0]["description"]
        assert "Secondary Warehouse" in transfer_events[0]["description"]

    def test_warehouse_to_kit_transfer(
        self,
        client,
        auth_headers_user,
        db_session,
        tool_with_warehouse,
        test_warehouse,
        test_kit,
        test_user,
    ):
        """Test warehouse to kit transfer appears in history"""
        transfer = WarehouseTransfer(
            from_warehouse_id=test_warehouse.id,
            to_warehouse_id=None,
            to_kit_id=test_kit.id,
            from_kit_id=None,
            item_type="tool",
            item_id=tool_with_warehouse.id,
            quantity=1,
            transfer_date=datetime.utcnow(),
            transferred_by_id=test_user.id,
            notes="Transfer to kit",
            status="completed",
        )
        db_session.add(transfer)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        transfer_events = [
            e
            for e in data["history"]
            if e["event_type"] == "warehouse_to_kit_transfer"
        ]
        assert len(transfer_events) == 1
        assert "Test Warehouse" in transfer_events[0]["description"]
        assert "Kit Q400-001" in transfer_events[0]["description"]

    def test_kit_to_warehouse_transfer(
        self,
        client,
        auth_headers_user,
        db_session,
        tool_with_warehouse,
        test_warehouse,
        test_kit,
        test_user,
    ):
        """Test kit to warehouse transfer appears in history"""
        transfer = WarehouseTransfer(
            from_warehouse_id=None,
            to_warehouse_id=test_warehouse.id,
            to_kit_id=None,
            from_kit_id=test_kit.id,
            item_type="tool",
            item_id=tool_with_warehouse.id,
            quantity=1,
            transfer_date=datetime.utcnow(),
            transferred_by_id=test_user.id,
            notes="Return from kit",
            status="completed",
        )
        db_session.add(transfer)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        transfer_events = [
            e for e in data["history"] if e["event_type"] == "kit_to_warehouse_transfer"
        ]
        assert len(transfer_events) == 1
        assert "Kit Q400-001" in transfer_events[0]["description"]
        assert "Test Warehouse" in transfer_events[0]["description"]

    def test_warehouse_transfer_with_child_lot(
        self,
        client,
        auth_headers_user,
        db_session,
        chemical_with_warehouse,
        test_warehouse,
        test_warehouse_2,
        test_user,
    ):
        """Test partial chemical transfer creates child lot reference"""
        # Create a child chemical at same time as transfer
        child = Chemical(
            part_number="CHEM-001",
            lot_number="LOT-251014-0001-1",
            description="Industrial Adhesive",
            manufacturer="ChemCorp",
            quantity=20,
            unit="ml",
            category="Adhesive",
            status="available",
            warehouse_id=test_warehouse_2.id,
            parent_lot_number="LOT-251014-0001",
            date_added=datetime.utcnow(),
        )
        db_session.add(child)

        transfer = WarehouseTransfer(
            from_warehouse_id=test_warehouse.id,
            to_warehouse_id=test_warehouse_2.id,
            item_type="chemical",
            item_id=chemical_with_warehouse.id,
            quantity=20,  # Less than parent's 100
            transfer_date=datetime.utcnow(),
            transferred_by_id=test_user.id,
            notes="Partial transfer",
            status="completed",
        )
        db_session.add(transfer)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={
                "identifier": "CHEM-001",
                "tracking_number": "LOT-251014-0001",
            },
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        transfer_events = [
            e
            for e in data["history"]
            if e["event_type"] == "warehouse_to_warehouse_transfer"
        ]
        assert len(transfer_events) == 1
        assert transfer_events[0]["details"]["child_lot_number"] == "LOT-251014-0001-1"

    def test_generic_warehouse_transfer(
        self, client, auth_headers_user, db_session, tool_with_warehouse, test_user
    ):
        """Test generic transfer (neither warehouse-to-warehouse nor kit involved)"""
        transfer = WarehouseTransfer(
            from_warehouse_id=None,
            to_warehouse_id=None,
            to_kit_id=None,
            from_kit_id=None,
            item_type="tool",
            item_id=tool_with_warehouse.id,
            quantity=1,
            transfer_date=datetime.utcnow(),
            transferred_by_id=test_user.id,
            notes="Generic transfer",
            status="completed",
        )
        db_session.add(transfer)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        transfer_events = [
            e for e in data["history"] if e["event_type"] == "transfer"
        ]
        assert len(transfer_events) >= 1


class TestKitTransferHistory:
    """Test kit transfer history tracking"""

    def test_kit_to_kit_transfer(
        self,
        client,
        auth_headers_user,
        db_session,
        tool_in_kit,
        test_kit,
        test_kit_2,
        test_user,
    ):
        """Test kit to kit transfer appears in history"""
        transfer = KitTransfer(
            item_type="tool",
            item_id=tool_in_kit.id,
            from_location_type="kit",
            from_location_id=test_kit.id,
            to_location_type="kit",
            to_location_id=test_kit_2.id,
            quantity=1.0,
            transferred_by=test_user.id,
            transfer_date=datetime.utcnow(),
            status="completed",
            notes="Kit to kit transfer",
        )
        db_session.add(transfer)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-KIT-001", "tracking_number": "SN-KIT-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        transfer_events = [
            e for e in data["history"] if e["event_type"] == "kit_to_kit_transfer"
        ]
        assert len(transfer_events) == 1
        assert "Kit Q400-001" in transfer_events[0]["description"]
        assert "Kit Q400-002" in transfer_events[0]["description"]

    def test_kit_to_warehouse_transfer_via_kit_transfer(
        self,
        client,
        auth_headers_user,
        db_session,
        tool_in_kit,
        test_kit,
        test_warehouse,
        test_user,
    ):
        """Test kit to warehouse transfer (KitTransfer model)"""
        transfer = KitTransfer(
            item_type="tool",
            item_id=tool_in_kit.id,
            from_location_type="kit",
            from_location_id=test_kit.id,
            to_location_type="warehouse",
            to_location_id=test_warehouse.id,
            quantity=1.0,
            transferred_by=test_user.id,
            transfer_date=datetime.utcnow(),
            status="completed",
            notes="Kit to warehouse",
        )
        db_session.add(transfer)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-KIT-001", "tracking_number": "SN-KIT-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        transfer_events = [
            e for e in data["history"] if e["event_type"] == "kit_to_warehouse_transfer"
        ]
        assert len(transfer_events) == 1
        assert "Kit Q400-001" in transfer_events[0]["description"]
        assert "Test Warehouse" in transfer_events[0]["description"]

    def test_warehouse_to_kit_transfer_via_kit_transfer(
        self,
        client,
        auth_headers_user,
        db_session,
        tool_in_kit,
        test_kit,
        test_warehouse,
        test_user,
    ):
        """Test warehouse to kit transfer (KitTransfer model)"""
        transfer = KitTransfer(
            item_type="tool",
            item_id=tool_in_kit.id,
            from_location_type="warehouse",
            from_location_id=test_warehouse.id,
            to_location_type="kit",
            to_location_id=test_kit.id,
            quantity=1.0,
            transferred_by=test_user.id,
            transfer_date=datetime.utcnow(),
            status="completed",
            notes="Warehouse to kit",
        )
        db_session.add(transfer)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-KIT-001", "tracking_number": "SN-KIT-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        transfer_events = [
            e for e in data["history"] if e["event_type"] == "warehouse_to_kit_transfer"
        ]
        assert len(transfer_events) == 1
        assert "Test Warehouse" in transfer_events[0]["description"]
        assert "Kit Q400-001" in transfer_events[0]["description"]

    def test_generic_kit_transfer(
        self, client, auth_headers_user, db_session, tool_in_kit, test_user
    ):
        """Test generic kit transfer (unknown location types)"""
        transfer = KitTransfer(
            item_type="tool",
            item_id=tool_in_kit.id,
            from_location_type="other",
            from_location_id=1,
            to_location_type="other",
            to_location_id=2,
            quantity=1.0,
            transferred_by=test_user.id,
            transfer_date=datetime.utcnow(),
            status="completed",
            notes="Generic transfer",
        )
        db_session.add(transfer)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-KIT-001", "tracking_number": "SN-KIT-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        transfer_events = [
            e for e in data["history"] if e["event_type"] == "transfer"
        ]
        assert len(transfer_events) >= 1

    def test_kit_transfer_with_child_lot(
        self,
        client,
        auth_headers_user,
        db_session,
        chemical_in_kit,
        test_kit,
        test_kit_2,
        test_user,
    ):
        """Test chemical kit transfer with child lot tracking"""
        # Create a child chemical
        child = Chemical(
            part_number="CHEM-KIT",
            lot_number="LOT-KIT-CHILD",
            description="Kit Chemical",
            manufacturer="KitChem",
            quantity=10,
            unit="ml",
            category="Solvent",
            status="available",
            warehouse_id=None,
            parent_lot_number="LOT-KIT",
            date_added=datetime.utcnow(),
        )
        db_session.add(child)

        transfer = KitTransfer(
            item_type="chemical",
            item_id=chemical_in_kit.id,
            from_location_type="kit",
            from_location_id=test_kit.id,
            to_location_type="kit",
            to_location_id=test_kit_2.id,
            quantity=10.0,
            transferred_by=test_user.id,
            transfer_date=datetime.utcnow(),
            status="completed",
            notes="Partial chemical transfer",
        )
        db_session.add(transfer)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "CHEM-KIT", "tracking_number": "LOT-KIT"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        transfer_events = [
            e for e in data["history"] if e["event_type"] == "kit_to_kit_transfer"
        ]
        assert len(transfer_events) == 1
        assert transfer_events[0]["details"]["child_lot_number"] == "LOT-KIT-CHILD"


class TestKitIssuanceHistory:
    """Test kit issuance history tracking"""

    def test_kit_issuance_by_serial_number(
        self, client, auth_headers_user, db_session, kit_expendable, test_kit, test_user
    ):
        """Test kit issuance with serial number"""
        issuance = KitIssuance(
            kit_id=test_kit.id,
            item_type="expendable",
            item_id=kit_expendable.id,
            issued_by=test_user.id,
            issued_to=test_user.id,
            part_number="EXP-001",
            serial_number="SN-EXP-001",
            lot_number=None,
            description="Expendable Item",
            quantity=2.0,
            purpose="Maintenance work",
            work_order="WO-12345",
            issued_date=datetime.utcnow(),
            notes="Used for repair",
        )
        db_session.add(issuance)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "EXP-001", "tracking_number": "SN-EXP-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        issuance_events = [
            e for e in data["history"] if e["event_type"] == "kit_issuance"
        ]
        assert len(issuance_events) == 1
        assert "Issued from kit Q400-001" in issuance_events[0]["description"]
        assert "Maintenance work" in issuance_events[0]["description"]
        assert issuance_events[0]["details"]["work_order"] == "WO-12345"

    def test_kit_issuance_by_lot_number(
        self, client, auth_headers_user, db_session, kit_expendable_lot, test_kit, test_user
    ):
        """Test kit issuance with lot number"""
        issuance = KitIssuance(
            kit_id=test_kit.id,
            item_type="expendable",
            item_id=kit_expendable_lot.id,
            issued_by=test_user.id,
            issued_to=None,
            part_number="EXP-002",
            serial_number=None,
            lot_number="LOT-EXP-002",
            description="Lot Tracked Expendable",
            quantity=5.0,
            purpose="Testing",
            work_order=None,
            issued_date=datetime.utcnow(),
            notes=None,
        )
        db_session.add(issuance)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "EXP-002", "tracking_number": "LOT-EXP-002"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        issuance_events = [
            e for e in data["history"] if e["event_type"] == "kit_issuance"
        ]
        assert len(issuance_events) == 1

    def test_kit_issuance_no_purpose(
        self, client, auth_headers_user, db_session, kit_expendable, test_kit, test_user
    ):
        """Test kit issuance with no purpose specified"""
        issuance = KitIssuance(
            kit_id=test_kit.id,
            item_type="expendable",
            item_id=kit_expendable.id,
            issued_by=test_user.id,
            part_number="EXP-001",
            serial_number="SN-EXP-001",
            description="Expendable Item",
            quantity=1.0,
            purpose=None,
            issued_date=datetime.utcnow(),
        )
        db_session.add(issuance)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "EXP-001", "tracking_number": "SN-EXP-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        issuance_events = [
            e for e in data["history"] if e["event_type"] == "kit_issuance"
        ]
        assert len(issuance_events) == 1
        assert "No purpose specified" in issuance_events[0]["description"]


class TestHistoryEventSorting:
    """Test that history events are properly sorted"""

    def test_events_sorted_by_timestamp(
        self, client, auth_headers_user, db_session, tool_with_warehouse, test_user
    ):
        """Test that history events are sorted by timestamp (newest first)"""
        # Create multiple events with different timestamps
        old_checkout = Checkout(
            tool_id=tool_with_warehouse.id,
            user_id=test_user.id,
            checkout_date=datetime.utcnow() - timedelta(days=10),
            return_date=datetime.utcnow() - timedelta(days=9),
        )
        db_session.add(old_checkout)

        recent_checkout = Checkout(
            tool_id=tool_with_warehouse.id,
            user_id=test_user.id,
            checkout_date=datetime.utcnow() - timedelta(hours=2),
        )
        db_session.add(recent_checkout)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        history = data["history"]
        timestamps = [
            event["timestamp"] for event in history if event["timestamp"]
        ]

        # Verify sorted in descending order (newest first)
        for i in range(len(timestamps) - 1):
            assert timestamps[i] >= timestamps[i + 1]


class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_tool_with_null_warehouse_no_kit_item(
        self, client, auth_headers_user, db_session, tool_without_warehouse
    ):
        """Test tool with no warehouse and no kit item returns unknown location"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-99999", "tracking_number": "SN-999"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["current_location"]["type"] == "unknown"
        assert data["current_location"]["name"] == "Unknown Location"

    def test_chemical_with_no_parent_lot(
        self, client, auth_headers_user, db_session, chemical_with_warehouse
    ):
        """Test chemical without parent lot returns null parent_lot"""
        response = client.post(
            "/api/history/lookup",
            json={
                "identifier": "CHEM-001",
                "tracking_number": "LOT-251014-0001",
            },
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["parent_lot"] is None
        assert data["child_lots"] == []

    def test_expendable_with_no_kit(self, client, auth_headers_user, db_session, test_kit_box):
        """Test expendable whose kit is deleted"""
        expendable = KitExpendable(
            kit_id=999999,  # Non-existent kit
            box_id=test_kit_box.id,
            part_number="EXP-ORPHAN",
            serial_number="SN-ORPHAN",
            tracking_type="serial",
            description="Orphan Expendable",
            quantity=1.0,
            unit="each",
            status="available",
        )
        db_session.add(expendable)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "EXP-ORPHAN", "tracking_number": "SN-ORPHAN"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["item_found"] is True
        assert data["item_details"]["kit_name"] is None
        assert data["current_location"]["name"] == "Unknown Kit"

    def test_history_with_missing_users(
        self, client, auth_headers_user, db_session, tool_with_warehouse
    ):
        """Test that history handles missing user records gracefully"""
        # Create transaction with non-existent user
        transaction = InventoryTransaction(
            item_type="tool",
            item_id=tool_with_warehouse.id,
            transaction_type="receipt",
            timestamp=datetime.utcnow(),
            user_id=999999,  # Non-existent user
            quantity_change=1,
            notes="Test",
        )
        db_session.add(transaction)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-12345", "tracking_number": "SN-001"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        # Should not crash, should show "Unknown User"
        receipt_events = [
            e for e in data["history"] if e["event_type"] == "receipt"
        ]
        assert len(receipt_events) == 1
        assert receipt_events[0]["user"] == "Unknown User"

    def test_whitespace_in_identifiers(
        self, client, auth_headers_user, db_session, tool_with_warehouse
    ):
        """Test that whitespace in identifiers is trimmed"""
        response = client.post(
            "/api/history/lookup",
            json={"identifier": "  T-12345  ", "tracking_number": "  SN-001  "},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["item_found"] is True

    def test_tool_without_calibration_dates(
        self, client, auth_headers_user, db_session, test_warehouse
    ):
        """Test tool without calibration dates"""
        tool = Tool(
            tool_number="T-NOCAL",
            serial_number="SN-NOCAL",
            description="No Calibration Tool",
            condition="Good",
            category="Hand Tools",
            status="available",
            warehouse_id=test_warehouse.id,
            requires_calibration=False,
        )
        db_session.add(tool)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "T-NOCAL", "tracking_number": "SN-NOCAL"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["item_found"] is True
        assert data["item_details"]["last_calibration_date"] is None
        assert data["item_details"]["next_calibration_date"] is None

    def test_chemical_without_expiration_date(
        self, client, auth_headers_user, db_session, test_warehouse
    ):
        """Test chemical without expiration date"""
        chemical = Chemical(
            part_number="CHEM-NOEXP",
            lot_number="LOT-NOEXP",
            description="No Expiration Chemical",
            manufacturer="Test",
            quantity=100,
            unit="each",
            category="General",
            status="available",
            warehouse_id=test_warehouse.id,
            expiration_date=None,
        )
        db_session.add(chemical)
        db_session.commit()

        response = client.post(
            "/api/history/lookup",
            json={"identifier": "CHEM-NOEXP", "tracking_number": "LOT-NOEXP"},
            headers=auth_headers_user,
        )
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["item_found"] is True
        assert data["item_details"]["expiration_date"] is None
