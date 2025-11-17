"""
Comprehensive tests for Expendable Management Routes

Tests all endpoints in routes_expendables.py:
- Add expendable to kit (POST /kits/<kit_id>/expendables)
- Update expendable (PUT /kits/<kit_id>/expendables/<expendable_id>)
- Remove expendable from kit (DELETE /kits/<kit_id>/expendables/<expendable_id>)
- Get expendable detail (GET /inventory/expendable/<expendable_id>/detail)
- Get expendable barcode (GET /expendables/<expendable_id>/barcode)
- Transfer expendable between kits (POST /transfers/kit-to-kit/expendable)

Note: Some endpoints in routes_expendables.py are shadowed by routes_kits.py
which registers the same paths first. These are tested directly through
function calls rather than HTTP requests.
"""

import json
import uuid
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask, g

from models import AuditLog, Expendable, User, db
from models_kits import AircraftType, Kit, KitBox, KitItem
from routes_expendables import (
    add_expendable_to_kit,
    generate_serial_number,
    remove_expendable_from_kit,
    update_expendable,
)


@pytest.fixture
def aircraft_type(db_session):
    """Create a test aircraft type"""
    at = AircraftType(name=f"TestAircraft-{uuid.uuid4().hex[:6]}", description="Test", is_active=True)
    db_session.add(at)
    db_session.commit()
    return at


@pytest.fixture
def kit_with_box(db_session, aircraft_type, materials_user):
    """Create a test kit with a box"""
    kit = Kit(
        name=f"TestKit-{uuid.uuid4().hex[:8]}",
        aircraft_type_id=aircraft_type.id,
        description="Test kit",
        status="active",
        created_by=materials_user.id
    )
    db_session.add(kit)
    db_session.flush()

    box = KitBox(
        kit_id=kit.id,
        box_number="Box1",
        box_type="expendable",
        description="Test box"
    )
    db_session.add(box)
    db_session.commit()

    return {"kit": kit, "box": box}


@pytest.fixture
def second_kit_with_box(db_session, aircraft_type, materials_user):
    """Create a second test kit with a box for transfer tests"""
    kit = Kit(
        name=f"SecondKit-{uuid.uuid4().hex[:8]}",
        aircraft_type_id=aircraft_type.id,
        description="Second kit",
        status="active",
        created_by=materials_user.id
    )
    db_session.add(kit)
    db_session.flush()

    box = KitBox(
        kit_id=kit.id,
        box_number="Box1",
        box_type="expendable",
        description="Second box"
    )
    db_session.add(box)
    db_session.commit()

    return {"kit": kit, "box": box}


@pytest.fixture
def expendable_in_kit(db_session, kit_with_box):
    """Create an expendable linked to a kit"""
    kit = kit_with_box["kit"]
    box = kit_with_box["box"]

    expendable = Expendable(
        part_number="EXP001",
        lot_number="LOT-TEST-001",
        description="Test Expendable",
        manufacturer="Test Manufacturer",
        quantity=10.0,
        unit="each",
        location="Slot A1",
        category="Testing",
        status="available",
        minimum_stock_level=5,
        notes="Test notes"
    )
    db_session.add(expendable)
    db_session.flush()

    kit_item = KitItem(
        kit_id=kit.id,
        box_id=box.id,
        item_type="expendable",
        item_id=expendable.id,
        part_number=expendable.part_number,
        lot_number=expendable.lot_number,
        description=expendable.description,
        quantity=expendable.quantity,
        location=expendable.location,
        status="available"
    )
    db_session.add(kit_item)
    db_session.commit()

    return {"expendable": expendable, "kit_item": kit_item}


@pytest.fixture
def serial_tracked_expendable(db_session, kit_with_box):
    """Create a serial-tracked expendable"""
    kit = kit_with_box["kit"]
    box = kit_with_box["box"]

    expendable = Expendable(
        part_number="SER001",
        serial_number="SN-TEST-001",
        description="Serial Tracked Expendable",
        manufacturer="Test Manufacturer",
        quantity=1.0,
        unit="each",
        location="Slot B2",
        category="Testing",
        status="available"
    )
    db_session.add(expendable)
    db_session.flush()

    kit_item = KitItem(
        kit_id=kit.id,
        box_id=box.id,
        item_type="expendable",
        item_id=expendable.id,
        part_number=expendable.part_number,
        serial_number=expendable.serial_number,
        description=expendable.description,
        quantity=expendable.quantity,
        location=expendable.location,
        status="available"
    )
    db_session.add(kit_item)
    db_session.commit()

    return {"expendable": expendable, "kit_item": kit_item}


class TestGenerateSerialNumber:
    """Tests for the generate_serial_number helper function"""

    def test_generates_valid_serial_number(self):
        """Test that serial number is generated with correct format"""
        serial = generate_serial_number("ABC123")
        assert serial.startswith("SN-ABC123-")
        # Should have timestamp after the part number
        parts = serial.split("-")
        assert len(parts) == 3
        assert parts[0] == "SN"
        assert parts[1] == "ABC123"
        # Timestamp should be numeric and 14 chars (YYYYMMDDHHMMSS)
        assert len(parts[2]) == 14
        assert parts[2].isdigit()

    def test_different_part_numbers_produce_different_serials(self):
        """Test that different part numbers produce different serial numbers"""
        serial1 = generate_serial_number("PART1")
        serial2 = generate_serial_number("PART2")
        assert "PART1" in serial1
        assert "PART2" in serial2
        assert serial1 != serial2


class TestAddExpendableToKitDirect:
    """Direct function tests for add_expendable_to_kit (bypassing shadowed route)"""

    @patch("auth.JWTManager.get_current_user")
    def test_add_lot_tracked_expendable_success(self, mock_get_user, client, kit_with_box, db_session):
        """Test adding a lot-tracked expendable to a kit"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        box = kit_with_box["box"]

        with client.application.test_request_context(
            json={
                "box_id": box.id,
                "part_number": "EXP-LOT-001",
                "description": "Lot Tracked Expendable",
                "quantity": 25.0,
                "unit": "oz",
                "tracking_type": "lot",
                "lot_number": "LOT-MANUAL-001",
                "manufacturer": "Acme Corp",
                "location": "Slot C3",
                "category": "Sealants",
                "minimum_stock_level": 10,
                "notes": "Handle with care"
            }
        ):
            response, status_code = add_expendable_to_kit(kit.id)
            result = response.get_json()

        assert status_code == 201
        assert result["message"] == "Expendable added to kit successfully"
        assert "expendable" in result
        assert "kit_item" in result

        # Check expendable details
        exp = result["expendable"]
        assert exp["part_number"] == "EXP-LOT-001"
        assert exp["lot_number"] == "LOT-MANUAL-001"
        assert exp["serial_number"] is None
        assert exp["quantity"] == 25.0
        assert exp["unit"] == "oz"
        assert exp["tracking_type"] == "lot"
        assert exp["manufacturer"] == "Acme Corp"
        assert exp["location"] == "Slot C3"
        assert exp["category"] == "Sealants"
        assert exp["minimum_stock_level"] == 10
        assert exp["notes"] == "Handle with care"

        # Check kit_item details
        kit_item = result["kit_item"]
        assert kit_item["kit_id"] == kit.id
        assert kit_item["box_id"] == box.id
        assert kit_item["item_type"] == "expendable"
        assert kit_item["part_number"] == "EXP-LOT-001"
        assert kit_item["lot_number"] == "LOT-MANUAL-001"

        # Verify audit log created
        audit_log = AuditLog.query.filter_by(action_type="expendable_added_to_kit").first()
        assert audit_log is not None
        assert "EXP-LOT-001" in audit_log.action_details

    @patch("auth.JWTManager.get_current_user")
    def test_add_serial_tracked_expendable_success(self, mock_get_user, client, kit_with_box, db_session):
        """Test adding a serial-tracked expendable to a kit"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        box = kit_with_box["box"]

        with client.application.test_request_context(
            json={
                "box_id": box.id,
                "part_number": "EXP-SER-001",
                "description": "Serial Tracked Expendable",
                "quantity": 1.0,
                "unit": "each",
                "tracking_type": "serial",
                "serial_number": "SN-MANUAL-001"
            }
        ):
            response, status_code = add_expendable_to_kit(kit.id)
            result = response.get_json()

        assert status_code == 201
        exp = result["expendable"]
        assert exp["serial_number"] == "SN-MANUAL-001"
        assert exp["lot_number"] is None
        assert exp["tracking_type"] == "serial"

    @patch("auth.JWTManager.get_current_user")
    def test_auto_generate_lot_number(self, mock_get_user, client, kit_with_box, db_session):
        """Test auto-generation of lot number when not provided"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        box = kit_with_box["box"]

        with client.application.test_request_context(
            json={
                "box_id": box.id,
                "part_number": "EXP-AUTO-LOT",
                "description": "Auto Lot Number",
                "quantity": 5.0,
                "unit": "ml",
                "tracking_type": "lot"
                # lot_number intentionally omitted
            }
        ):
            response, status_code = add_expendable_to_kit(kit.id)
            result = response.get_json()

        assert status_code == 201
        exp = result["expendable"]
        assert exp["lot_number"] is not None
        assert exp["lot_number"].startswith("LOT-")
        assert exp["serial_number"] is None

    @patch("auth.JWTManager.get_current_user")
    def test_auto_generate_serial_number(self, mock_get_user, client, kit_with_box, db_session):
        """Test auto-generation of serial number when not provided"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        box = kit_with_box["box"]

        with client.application.test_request_context(
            json={
                "box_id": box.id,
                "part_number": "EXP-AUTO-SER",
                "description": "Auto Serial Number",
                "quantity": 1.0,
                "unit": "each",
                "tracking_type": "serial"
                # serial_number intentionally omitted
            }
        ):
            response, status_code = add_expendable_to_kit(kit.id)
            result = response.get_json()

        assert status_code == 201
        exp = result["expendable"]
        assert exp["serial_number"] is not None
        assert exp["serial_number"].startswith("SN-EXP-AUTO-SER-")
        assert exp["lot_number"] is None

    @patch("auth.JWTManager.get_current_user")
    def test_missing_required_field_part_number(self, mock_get_user, client, kit_with_box):
        """Test validation error when part_number is missing"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        box = kit_with_box["box"]

        with client.application.test_request_context(
            json={
                "box_id": box.id,
                "description": "Test",
                "quantity": 1.0,
                "unit": "each",
                "tracking_type": "lot"
            }
        ):
            response, status_code = add_expendable_to_kit(kit.id)
            result = response.get_json()

        assert status_code == 400
        assert "part_number" in result["error"]

    @patch("auth.JWTManager.get_current_user")
    def test_missing_required_field_box_id(self, mock_get_user, client, kit_with_box):
        """Test validation error when box_id is missing"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]

        with client.application.test_request_context(
            json={
                "part_number": "EXP001",
                "description": "Test",
                "quantity": 1.0,
                "unit": "each",
                "tracking_type": "lot"
            }
        ):
            response, status_code = add_expendable_to_kit(kit.id)
            result = response.get_json()

        assert status_code == 400
        assert "box_id" in result["error"]

    @patch("auth.JWTManager.get_current_user")
    def test_missing_required_field_description(self, mock_get_user, client, kit_with_box):
        """Test validation error when description is missing"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        box = kit_with_box["box"]

        with client.application.test_request_context(
            json={
                "box_id": box.id,
                "part_number": "EXP001",
                "quantity": 1.0,
                "unit": "each",
                "tracking_type": "lot"
            }
        ):
            response, status_code = add_expendable_to_kit(kit.id)
            result = response.get_json()

        assert status_code == 400
        assert "description" in result["error"]

    @patch("auth.JWTManager.get_current_user")
    def test_missing_required_field_quantity(self, mock_get_user, client, kit_with_box):
        """Test validation error when quantity is missing"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        box = kit_with_box["box"]

        with client.application.test_request_context(
            json={
                "box_id": box.id,
                "part_number": "EXP001",
                "description": "Test",
                "unit": "each",
                "tracking_type": "lot"
            }
        ):
            response, status_code = add_expendable_to_kit(kit.id)
            result = response.get_json()

        assert status_code == 400
        assert "quantity" in result["error"]

    @patch("auth.JWTManager.get_current_user")
    def test_missing_required_field_unit(self, mock_get_user, client, kit_with_box):
        """Test validation error when unit is missing"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        box = kit_with_box["box"]

        with client.application.test_request_context(
            json={
                "box_id": box.id,
                "part_number": "EXP001",
                "description": "Test",
                "quantity": 1.0,
                "tracking_type": "lot"
            }
        ):
            response, status_code = add_expendable_to_kit(kit.id)
            result = response.get_json()

        assert status_code == 400
        assert "unit" in result["error"]

    @patch("auth.JWTManager.get_current_user")
    def test_missing_required_field_tracking_type(self, mock_get_user, client, kit_with_box):
        """Test validation error when tracking_type is missing"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        box = kit_with_box["box"]

        with client.application.test_request_context(
            json={
                "box_id": box.id,
                "part_number": "EXP001",
                "description": "Test",
                "quantity": 1.0,
                "unit": "each"
            }
        ):
            response, status_code = add_expendable_to_kit(kit.id)
            result = response.get_json()

        assert status_code == 400
        assert "tracking_type" in result["error"]

    @patch("auth.JWTManager.get_current_user")
    def test_invalid_tracking_type(self, mock_get_user, client, kit_with_box):
        """Test validation error for invalid tracking type"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        box = kit_with_box["box"]

        with client.application.test_request_context(
            json={
                "box_id": box.id,
                "part_number": "EXP001",
                "description": "Test",
                "quantity": 1.0,
                "unit": "each",
                "tracking_type": "invalid"
            }
        ):
            response, status_code = add_expendable_to_kit(kit.id)
            result = response.get_json()

        assert status_code == 400
        assert "lot" in result["error"] or "serial" in result["error"]

    @patch("auth.JWTManager.get_current_user")
    def test_box_not_belongs_to_kit(self, mock_get_user, client, kit_with_box, second_kit_with_box):
        """Test validation error when box doesn't belong to kit"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        other_box = second_kit_with_box["box"]

        with client.application.test_request_context(
            json={
                "box_id": other_box.id,
                "part_number": "EXP001",
                "description": "Test",
                "quantity": 1.0,
                "unit": "each",
                "tracking_type": "lot"
            }
        ):
            response, status_code = add_expendable_to_kit(kit.id)
            result = response.get_json()

        assert status_code == 400
        assert "Box does not belong to this kit" in result["error"]

    @patch("auth.JWTManager.get_current_user")
    def test_default_category_applied(self, mock_get_user, client, kit_with_box, db_session):
        """Test that default category 'General' is applied when not provided"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        box = kit_with_box["box"]

        with client.application.test_request_context(
            json={
                "box_id": box.id,
                "part_number": "EXP-DEFAULT",
                "description": "Default Category Test",
                "quantity": 1.0,
                "unit": "each",
                "tracking_type": "lot"
            }
        ):
            response, status_code = add_expendable_to_kit(kit.id)
            result = response.get_json()

        assert status_code == 201
        assert result["expendable"]["category"] == "General"

    @patch("auth.JWTManager.get_current_user")
    def test_empty_json_body(self, mock_get_user, client, kit_with_box):
        """Test handling of empty JSON body"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]

        with client.application.test_request_context(json={}):
            response, status_code = add_expendable_to_kit(kit.id)
            result = response.get_json()

        assert status_code == 400

    @patch("auth.JWTManager.get_current_user")
    @patch("routes_expendables.Expendable")
    def test_handles_value_error_on_creation(self, mock_expendable_class, mock_get_user, client, kit_with_box):
        """Test handling of ValueError during expendable creation (e.g., validation error)"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        mock_expendable_class.side_effect = ValueError("Expendable must have EITHER serial number OR lot number")
        kit = kit_with_box["kit"]
        box = kit_with_box["box"]

        with client.application.test_request_context(
            json={
                "box_id": box.id,
                "part_number": "EXP-FAIL",
                "description": "Test",
                "quantity": 1.0,
                "unit": "each",
                "tracking_type": "lot",
                "lot_number": "LOT-001"
            }
        ):
            response, status_code = add_expendable_to_kit(kit.id)
            result = response.get_json()

        assert status_code == 400
        assert "error" in result

    @patch("auth.JWTManager.get_current_user")
    @patch("routes_expendables.db.session.add")
    def test_handles_general_exception(self, mock_add, mock_get_user, client, kit_with_box):
        """Test handling of general exceptions during expendable creation"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        mock_add.side_effect = Exception("Database connection error")
        kit = kit_with_box["kit"]
        box = kit_with_box["box"]

        with client.application.test_request_context(
            json={
                "box_id": box.id,
                "part_number": "EXP-ERR",
                "description": "Test",
                "quantity": 1.0,
                "unit": "each",
                "tracking_type": "lot",
                "lot_number": "LOT-ERR"
            }
        ):
            # The @handle_errors decorator catches exceptions and returns error response
            response, status_code = add_expendable_to_kit(kit.id)
            result = response.get_json()

        # General exceptions result in 500 status code
        assert status_code == 500
        assert "error" in result


class TestUpdateExpendableDirect:
    """Direct function tests for update_expendable (bypassing shadowed route)"""

    @patch("auth.JWTManager.get_current_user")
    def test_update_quantity_success(self, mock_get_user, client, kit_with_box, expendable_in_kit, db_session):
        """Test updating expendable quantity"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        expendable = expendable_in_kit["expendable"]

        with client.application.test_request_context(json={"quantity": 15.0}):
            response, status_code = update_expendable(kit.id, expendable.id)
            result = response.get_json()

        assert status_code == 200
        assert result["message"] == "Expendable updated successfully"
        assert result["expendable"]["quantity"] == 15.0
        assert result["kit_item"]["quantity"] == 15.0

    @patch("auth.JWTManager.get_current_user")
    def test_update_multiple_fields(self, mock_get_user, client, kit_with_box, expendable_in_kit, db_session):
        """Test updating multiple expendable fields at once"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        expendable = expendable_in_kit["expendable"]

        with client.application.test_request_context(
            json={
                "quantity": 20.0,
                "location": "New Location",
                "status": "low_stock",
                "minimum_stock_level": 8,
                "notes": "Updated notes"
            }
        ):
            response, status_code = update_expendable(kit.id, expendable.id)
            result = response.get_json()

        assert status_code == 200
        exp = result["expendable"]
        assert exp["quantity"] == 20.0
        assert exp["location"] == "New Location"
        assert exp["status"] == "low_stock"
        assert exp["minimum_stock_level"] == 8
        assert exp["notes"] == "Updated notes"

        kit_item = result["kit_item"]
        assert kit_item["quantity"] == 20.0
        assert kit_item["location"] == "New Location"
        assert kit_item["status"] == "low_stock"

    @patch("auth.JWTManager.get_current_user")
    def test_update_location_only(self, mock_get_user, client, kit_with_box, expendable_in_kit, db_session):
        """Test updating only the location"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        expendable = expendable_in_kit["expendable"]

        with client.application.test_request_context(json={"location": "Slot D4"}):
            response, status_code = update_expendable(kit.id, expendable.id)
            result = response.get_json()

        assert status_code == 200
        assert result["expendable"]["location"] == "Slot D4"

    @patch("auth.JWTManager.get_current_user")
    def test_update_status_only(self, mock_get_user, client, kit_with_box, expendable_in_kit, db_session):
        """Test updating only the status"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        expendable = expendable_in_kit["expendable"]

        with client.application.test_request_context(json={"status": "out_of_stock"}):
            response, status_code = update_expendable(kit.id, expendable.id)
            result = response.get_json()

        assert status_code == 200
        assert result["expendable"]["status"] == "out_of_stock"
        assert result["kit_item"]["status"] == "out_of_stock"

    @patch("auth.JWTManager.get_current_user")
    def test_update_notes_only(self, mock_get_user, client, kit_with_box, expendable_in_kit, db_session):
        """Test updating only the notes"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        expendable = expendable_in_kit["expendable"]

        with client.application.test_request_context(json={"notes": "New important notes"}):
            response, status_code = update_expendable(kit.id, expendable.id)
            result = response.get_json()

        assert status_code == 200
        assert result["expendable"]["notes"] == "New important notes"

    @patch("auth.JWTManager.get_current_user")
    def test_update_minimum_stock_level(self, mock_get_user, client, kit_with_box, expendable_in_kit, db_session):
        """Test updating minimum stock level"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        expendable = expendable_in_kit["expendable"]

        with client.application.test_request_context(json={"minimum_stock_level": 15}):
            response, status_code = update_expendable(kit.id, expendable.id)
            result = response.get_json()

        assert status_code == 200
        assert result["expendable"]["minimum_stock_level"] == 15

    @patch("auth.JWTManager.get_current_user")
    def test_expendable_not_in_kit(self, mock_get_user, client, kit_with_box, second_kit_with_box, db_session):
        """Test error when expendable is not in the specified kit"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        other_kit = second_kit_with_box["kit"]
        other_box = second_kit_with_box["box"]

        # Create expendable in other kit
        other_expendable = Expendable(
            part_number="OTHER001",
            lot_number="LOT-OTHER",
            description="Other Expendable",
            quantity=5.0,
            unit="each"
        )
        db_session.add(other_expendable)
        db_session.flush()

        other_kit_item = KitItem(
            kit_id=other_kit.id,
            box_id=other_box.id,
            item_type="expendable",
            item_id=other_expendable.id,
            part_number=other_expendable.part_number,
            quantity=5.0
        )
        db_session.add(other_kit_item)
        db_session.commit()

        with client.application.test_request_context(json={"quantity": 10.0}):
            response, status_code = update_expendable(kit.id, other_expendable.id)
            result = response.get_json()

        assert status_code == 400
        assert "Expendable not found in this kit" in result["error"]

    @patch("auth.JWTManager.get_current_user")
    def test_audit_log_created(self, mock_get_user, client, kit_with_box, expendable_in_kit, db_session):
        """Test that audit log is created on update"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        expendable = expendable_in_kit["expendable"]

        # Clear existing audit logs
        AuditLog.query.filter_by(action_type="expendable_updated").delete()
        db_session.commit()

        with client.application.test_request_context(json={"quantity": 25.0}):
            response, status_code = update_expendable(kit.id, expendable.id)

        assert status_code == 200

        audit_log = AuditLog.query.filter_by(action_type="expendable_updated").first()
        assert audit_log is not None
        assert expendable.part_number in audit_log.action_details
        assert kit.name in audit_log.action_details

    @patch("auth.JWTManager.get_current_user")
    def test_empty_update_body(self, mock_get_user, client, kit_with_box, expendable_in_kit, db_session):
        """Test updating with empty body (no changes)"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        expendable = expendable_in_kit["expendable"]
        original_quantity = expendable.quantity

        with client.application.test_request_context(json={}):
            response, status_code = update_expendable(kit.id, expendable.id)
            result = response.get_json()

        assert status_code == 200
        # Quantity should remain unchanged
        assert result["expendable"]["quantity"] == original_quantity


class TestRemoveExpendableFromKitDirect:
    """Direct function tests for remove_expendable_from_kit (bypassing shadowed route)"""

    @patch("auth.JWTManager.get_current_user")
    def test_remove_success(self, mock_get_user, client, kit_with_box, expendable_in_kit, db_session):
        """Test successfully removing an expendable from a kit"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        expendable = expendable_in_kit["expendable"]
        expendable_id = expendable.id

        with client.application.test_request_context():
            response, status_code = remove_expendable_from_kit(kit.id, expendable.id)
            result = response.get_json()

        assert status_code == 200
        assert result["message"] == "Expendable removed from kit successfully"

        # Verify expendable is deleted
        deleted_exp = Expendable.query.get(expendable_id)
        assert deleted_exp is None

        # Verify kit_item is deleted
        kit_item = KitItem.query.filter_by(item_type="expendable", item_id=expendable_id).first()
        assert kit_item is None

    @patch("auth.JWTManager.get_current_user")
    def test_audit_log_created_on_removal(self, mock_get_user, client, kit_with_box, expendable_in_kit, db_session):
        """Test that audit log is created when removing expendable"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        expendable = expendable_in_kit["expendable"]
        part_number = expendable.part_number

        # Clear existing audit logs
        AuditLog.query.filter_by(action_type="expendable_removed_from_kit").delete()
        db_session.commit()

        with client.application.test_request_context():
            response, status_code = remove_expendable_from_kit(kit.id, expendable.id)

        assert status_code == 200

        audit_log = AuditLog.query.filter_by(action_type="expendable_removed_from_kit").first()
        assert audit_log is not None
        assert part_number in audit_log.action_details
        assert kit.name in audit_log.action_details

    @patch("auth.JWTManager.get_current_user")
    def test_expendable_not_in_kit(self, mock_get_user, client, kit_with_box, second_kit_with_box, db_session):
        """Test error when expendable is not in the specified kit"""
        mock_get_user.return_value = {"user_id": 1, "is_admin": True, "department": "Materials"}
        kit = kit_with_box["kit"]
        other_kit = second_kit_with_box["kit"]
        other_box = second_kit_with_box["box"]

        # Create expendable in other kit
        other_expendable = Expendable(
            part_number="OTHER002",
            serial_number="SN-OTHER-002",
            description="Other Expendable",
            quantity=1.0,
            unit="each"
        )
        db_session.add(other_expendable)
        db_session.flush()

        other_kit_item = KitItem(
            kit_id=other_kit.id,
            box_id=other_box.id,
            item_type="expendable",
            item_id=other_expendable.id,
            part_number=other_expendable.part_number,
            quantity=1.0
        )
        db_session.add(other_kit_item)
        db_session.commit()

        with client.application.test_request_context():
            response, status_code = remove_expendable_from_kit(kit.id, other_expendable.id)
            result = response.get_json()

        assert status_code == 400
        assert "Expendable not found in this kit" in result["error"]


class TestGetExpendableDetail:
    """Tests for GET /inventory/expendable/<expendable_id>/detail"""

    def test_get_lot_tracked_expendable_detail(self, client, auth_headers_user, kit_with_box, expendable_in_kit):
        """Test getting details for a lot-tracked expendable"""
        kit = kit_with_box["kit"]
        box = kit_with_box["box"]
        expendable = expendable_in_kit["expendable"]

        response = client.get(
            f"/api/inventory/expendable/{expendable.id}/detail",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        result = json.loads(response.data)

        assert result["id"] == expendable.id
        assert result["part_number"] == "EXP001"
        assert result["description"] == "Test Expendable"
        assert result["manufacturer"] == "Test Manufacturer"
        assert result["lot_number"] == "LOT-TEST-001"
        assert result["serial_number"] is None
        assert result["tracking_type"] == "lot"
        assert result["quantity"] == 10.0
        assert result["unit"] == "each"
        assert result["location"] == "Slot A1"
        assert result["category"] == "Testing"
        assert result["status"] == "available"
        assert result["minimum_stock_level"] == 5
        assert result["notes"] == "Test notes"
        assert result["warehouse_id"] is None
        assert result["date_added"] is not None

        # Check kit locations
        assert len(result["kit_locations"]) == 1
        kit_loc = result["kit_locations"][0]
        assert kit_loc["kit_id"] == kit.id
        assert kit_loc["kit_name"] == kit.name
        assert kit_loc["box_id"] == box.id
        assert kit_loc["box_number"] == "Box1"
        assert kit_loc["quantity"] == 10.0
        assert kit_loc["status"] == "available"

    def test_get_serial_tracked_expendable_detail(self, client, auth_headers_user, serial_tracked_expendable):
        """Test getting details for a serial-tracked expendable"""
        expendable = serial_tracked_expendable["expendable"]

        response = client.get(
            f"/api/inventory/expendable/{expendable.id}/detail",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        result = json.loads(response.data)

        assert result["serial_number"] == "SN-TEST-001"
        assert result["lot_number"] is None
        assert result["tracking_type"] == "serial"

    def test_expendable_with_no_kit_locations(self, client, auth_headers_user, db_session):
        """Test expendable that is not in any kit"""
        # Create expendable without kit association
        expendable = Expendable(
            part_number="ORPHAN001",
            lot_number="LOT-ORPHAN",
            description="Orphan Expendable",
            quantity=5.0,
            unit="each"
        )
        db_session.add(expendable)
        db_session.commit()

        response = client.get(
            f"/api/inventory/expendable/{expendable.id}/detail",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        result = json.loads(response.data)
        assert result["kit_locations"] == []

    def test_expendable_in_multiple_kits(self, client, auth_headers_user, kit_with_box, second_kit_with_box, db_session):
        """Test expendable that appears in multiple kits (edge case)"""
        kit1 = kit_with_box["kit"]
        box1 = kit_with_box["box"]
        kit2 = second_kit_with_box["kit"]
        box2 = second_kit_with_box["box"]

        # Create expendable
        expendable = Expendable(
            part_number="MULTI001",
            lot_number="LOT-MULTI",
            description="Multi-kit Expendable",
            quantity=20.0,
            unit="each"
        )
        db_session.add(expendable)
        db_session.flush()

        # Add to first kit
        kit_item1 = KitItem(
            kit_id=kit1.id,
            box_id=box1.id,
            item_type="expendable",
            item_id=expendable.id,
            part_number=expendable.part_number,
            quantity=10.0
        )
        db_session.add(kit_item1)

        # Add to second kit
        kit_item2 = KitItem(
            kit_id=kit2.id,
            box_id=box2.id,
            item_type="expendable",
            item_id=expendable.id,
            part_number=expendable.part_number,
            quantity=10.0
        )
        db_session.add(kit_item2)
        db_session.commit()

        response = client.get(
            f"/api/inventory/expendable/{expendable.id}/detail",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        result = json.loads(response.data)
        assert len(result["kit_locations"]) == 2

    def test_expendable_not_found(self, client, auth_headers_user):
        """Test 404 error when expendable doesn't exist"""
        response = client.get(
            "/api/inventory/expendable/99999/detail",
            headers=auth_headers_user
        )

        assert response.status_code == 404

    def test_unauthenticated_request(self, client, expendable_in_kit):
        """Test authentication required for getting expendable details"""
        expendable = expendable_in_kit["expendable"]

        response = client.get(
            f"/api/inventory/expendable/{expendable.id}/detail"
        )

        assert response.status_code == 401

    def test_any_authenticated_user_can_access(self, client, user_auth_headers, expendable_in_kit):
        """Test that any authenticated user (not just Materials) can view details"""
        expendable = expendable_in_kit["expendable"]

        response = client.get(
            f"/api/inventory/expendable/{expendable.id}/detail",
            headers=user_auth_headers
        )

        assert response.status_code == 200


class TestGetExpendableBarcode:
    """Tests for GET /expendables/<expendable_id>/barcode"""

    def test_get_barcode_for_lot_tracked(self, client, auth_headers_user, expendable_in_kit):
        """Test getting barcode data for lot-tracked expendable"""
        expendable = expendable_in_kit["expendable"]

        response = client.get(
            f"/api/expendables/{expendable.id}/barcode",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        result = json.loads(response.data)

        assert result["barcode_data"] == "EXP001-LOT-LOT-TEST-001"
        assert "/expendable-view/" in result["qr_url"]
        assert str(expendable.id) in result["qr_url"]
        assert result["part_number"] == "EXP001"
        assert result["lot_number"] == "LOT-TEST-001"
        assert result["serial_number"] is None
        assert result["description"] == "Test Expendable"
        assert result["quantity"] == 10.0
        assert result["unit"] == "each"
        assert result["location"] == "Slot A1"
        assert result["category"] == "Testing"
        assert result["date_added"] is not None

    def test_get_barcode_for_serial_tracked(self, client, auth_headers_user, serial_tracked_expendable):
        """Test getting barcode data for serial-tracked expendable"""
        expendable = serial_tracked_expendable["expendable"]

        response = client.get(
            f"/api/expendables/{expendable.id}/barcode",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        result = json.loads(response.data)

        assert result["barcode_data"] == "SER001-SN-TEST-001"
        assert result["serial_number"] == "SN-TEST-001"
        assert result["lot_number"] is None

    def test_expendable_not_found(self, client, auth_headers_user):
        """Test 404 error when expendable doesn't exist"""
        response = client.get(
            "/api/expendables/99999/barcode",
            headers=auth_headers_user
        )

        assert response.status_code == 404

    def test_unauthenticated_request(self, client, expendable_in_kit):
        """Test authentication required for getting barcode"""
        expendable = expendable_in_kit["expendable"]

        response = client.get(
            f"/api/expendables/{expendable.id}/barcode"
        )

        assert response.status_code == 401

    def test_qr_url_format(self, client, auth_headers_user, expendable_in_kit):
        """Test that QR URL has correct format"""
        expendable = expendable_in_kit["expendable"]

        response = client.get(
            f"/api/expendables/{expendable.id}/barcode",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        result = json.loads(response.data)

        # QR URL should end with /expendable-view/{id}
        assert result["qr_url"].endswith(f"/expendable-view/{expendable.id}")


class TestTransferExpendableBetweenKits:
    """Tests for POST /transfers/kit-to-kit/expendable"""

    def test_transfer_success(self, client, auth_headers_materials, kit_with_box, second_kit_with_box, expendable_in_kit, db_session):
        """Test successfully transferring an expendable between kits"""
        from_kit = kit_with_box["kit"]
        to_kit = second_kit_with_box["kit"]
        to_box = second_kit_with_box["box"]
        expendable = expendable_in_kit["expendable"]

        data = {
            "from_kit_id": from_kit.id,
            "to_kit_id": to_kit.id,
            "to_box_id": to_box.id,
            "expendable_id": expendable.id
        }

        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json=data,
            headers=auth_headers_materials
        )

        assert response.status_code == 200
        result = json.loads(response.data)

        assert result["message"] == "Expendable transferred successfully"
        assert result["from_kit"] == from_kit.name
        assert result["to_kit"] == to_kit.name
        assert result["to_box"] == to_box.box_number

        # Verify expendable is no longer in source kit
        old_kit_item = KitItem.query.filter_by(kit_id=from_kit.id, item_id=expendable.id).first()
        assert old_kit_item is None

        # Verify expendable is in destination kit
        new_kit_item = KitItem.query.filter_by(kit_id=to_kit.id, item_id=expendable.id).first()
        assert new_kit_item is not None
        assert new_kit_item.box_id == to_box.id

    def test_transfer_with_location_update(self, client, auth_headers_materials, kit_with_box, second_kit_with_box, expendable_in_kit):
        """Test transferring with location update"""
        from_kit = kit_with_box["kit"]
        to_kit = second_kit_with_box["kit"]
        to_box = second_kit_with_box["box"]
        expendable = expendable_in_kit["expendable"]

        data = {
            "from_kit_id": from_kit.id,
            "to_kit_id": to_kit.id,
            "to_box_id": to_box.id,
            "expendable_id": expendable.id,
            "location": "New Slot E5"
        }

        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json=data,
            headers=auth_headers_materials
        )

        assert response.status_code == 200
        result = json.loads(response.data)

        # Check location was updated
        new_kit_item = KitItem.query.filter_by(kit_id=to_kit.id, item_id=expendable.id).first()
        assert new_kit_item.location == "New Slot E5"

        # Check expendable location also updated
        updated_exp = Expendable.query.get(expendable.id)
        assert updated_exp.location == "New Slot E5"

    def test_transfer_serial_tracked_expendable(self, client, auth_headers_materials, kit_with_box, second_kit_with_box, serial_tracked_expendable, db_session):
        """Test transferring a serial-tracked expendable"""
        from_kit = kit_with_box["kit"]
        to_kit = second_kit_with_box["kit"]
        to_box = second_kit_with_box["box"]
        expendable = serial_tracked_expendable["expendable"]

        data = {
            "from_kit_id": from_kit.id,
            "to_kit_id": to_kit.id,
            "to_box_id": to_box.id,
            "expendable_id": expendable.id
        }

        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json=data,
            headers=auth_headers_materials
        )

        assert response.status_code == 200

        # Verify audit log mentions serial number
        audit_log = AuditLog.query.filter_by(action_type="expendable_transferred_between_kits").order_by(AuditLog.id.desc()).first()
        assert audit_log is not None
        assert "serial" in audit_log.action_details

    def test_missing_required_field_from_kit_id(self, client, auth_headers_materials, second_kit_with_box, expendable_in_kit):
        """Test validation error when from_kit_id is missing"""
        to_kit = second_kit_with_box["kit"]
        to_box = second_kit_with_box["box"]
        expendable = expendable_in_kit["expendable"]

        data = {
            # from_kit_id missing
            "to_kit_id": to_kit.id,
            "to_box_id": to_box.id,
            "expendable_id": expendable.id
        }

        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json=data,
            headers=auth_headers_materials
        )

        assert response.status_code == 400
        result = json.loads(response.data)
        assert "from_kit_id" in result["error"]

    def test_missing_required_field_to_kit_id(self, client, auth_headers_materials, kit_with_box, second_kit_with_box, expendable_in_kit):
        """Test validation error when to_kit_id is missing"""
        from_kit = kit_with_box["kit"]
        to_box = second_kit_with_box["box"]
        expendable = expendable_in_kit["expendable"]

        data = {
            "from_kit_id": from_kit.id,
            # to_kit_id missing
            "to_box_id": to_box.id,
            "expendable_id": expendable.id
        }

        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json=data,
            headers=auth_headers_materials
        )

        assert response.status_code == 400
        result = json.loads(response.data)
        assert "to_kit_id" in result["error"]

    def test_missing_required_field_to_box_id(self, client, auth_headers_materials, kit_with_box, second_kit_with_box, expendable_in_kit):
        """Test validation error when to_box_id is missing"""
        from_kit = kit_with_box["kit"]
        to_kit = second_kit_with_box["kit"]
        expendable = expendable_in_kit["expendable"]

        data = {
            "from_kit_id": from_kit.id,
            "to_kit_id": to_kit.id,
            # to_box_id missing
            "expendable_id": expendable.id
        }

        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json=data,
            headers=auth_headers_materials
        )

        assert response.status_code == 400
        result = json.loads(response.data)
        assert "to_box_id" in result["error"]

    def test_missing_required_field_expendable_id(self, client, auth_headers_materials, kit_with_box, second_kit_with_box):
        """Test validation error when expendable_id is missing"""
        from_kit = kit_with_box["kit"]
        to_kit = second_kit_with_box["kit"]
        to_box = second_kit_with_box["box"]

        data = {
            "from_kit_id": from_kit.id,
            "to_kit_id": to_kit.id,
            "to_box_id": to_box.id
            # expendable_id missing
        }

        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json=data,
            headers=auth_headers_materials
        )

        assert response.status_code == 400
        result = json.loads(response.data)
        assert "expendable_id" in result["error"]

    def test_box_not_belongs_to_destination_kit(self, client, auth_headers_materials, kit_with_box, second_kit_with_box, expendable_in_kit):
        """Test error when destination box doesn't belong to destination kit"""
        from_kit = kit_with_box["kit"]
        to_kit = second_kit_with_box["kit"]
        wrong_box = kit_with_box["box"]  # This box belongs to from_kit, not to_kit
        expendable = expendable_in_kit["expendable"]

        data = {
            "from_kit_id": from_kit.id,
            "to_kit_id": to_kit.id,
            "to_box_id": wrong_box.id,  # Wrong kit's box
            "expendable_id": expendable.id
        }

        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json=data,
            headers=auth_headers_materials
        )

        assert response.status_code == 400
        result = json.loads(response.data)
        assert "Box does not belong to the destination kit" in result["error"]

    def test_expendable_not_in_source_kit(self, client, auth_headers_materials, kit_with_box, second_kit_with_box, db_session):
        """Test error when expendable is not in the source kit"""
        from_kit = kit_with_box["kit"]
        to_kit = second_kit_with_box["kit"]
        to_box = second_kit_with_box["box"]

        # Create expendable that's not in any kit
        orphan_expendable = Expendable(
            part_number="ORPHAN002",
            lot_number="LOT-ORPHAN-002",
            description="Orphan",
            quantity=1.0,
            unit="each"
        )
        db_session.add(orphan_expendable)
        db_session.commit()

        data = {
            "from_kit_id": from_kit.id,
            "to_kit_id": to_kit.id,
            "to_box_id": to_box.id,
            "expendable_id": orphan_expendable.id
        }

        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json=data,
            headers=auth_headers_materials
        )

        assert response.status_code == 400
        result = json.loads(response.data)
        assert "Expendable not found in source kit" in result["error"]

    def test_source_kit_not_found(self, client, auth_headers_materials, second_kit_with_box, expendable_in_kit):
        """Test 404 error when source kit doesn't exist"""
        to_kit = second_kit_with_box["kit"]
        to_box = second_kit_with_box["box"]
        expendable = expendable_in_kit["expendable"]

        data = {
            "from_kit_id": 99999,
            "to_kit_id": to_kit.id,
            "to_box_id": to_box.id,
            "expendable_id": expendable.id
        }

        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json=data,
            headers=auth_headers_materials
        )

        assert response.status_code == 404

    def test_destination_kit_not_found(self, client, auth_headers_materials, kit_with_box, second_kit_with_box, expendable_in_kit):
        """Test 404 error when destination kit doesn't exist"""
        from_kit = kit_with_box["kit"]
        to_box = second_kit_with_box["box"]
        expendable = expendable_in_kit["expendable"]

        data = {
            "from_kit_id": from_kit.id,
            "to_kit_id": 99999,
            "to_box_id": to_box.id,
            "expendable_id": expendable.id
        }

        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json=data,
            headers=auth_headers_materials
        )

        assert response.status_code == 404

    def test_destination_box_not_found(self, client, auth_headers_materials, kit_with_box, second_kit_with_box, expendable_in_kit):
        """Test 404 error when destination box doesn't exist"""
        from_kit = kit_with_box["kit"]
        to_kit = second_kit_with_box["kit"]
        expendable = expendable_in_kit["expendable"]

        data = {
            "from_kit_id": from_kit.id,
            "to_kit_id": to_kit.id,
            "to_box_id": 99999,
            "expendable_id": expendable.id
        }

        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json=data,
            headers=auth_headers_materials
        )

        assert response.status_code == 404

    def test_expendable_not_found(self, client, auth_headers_materials, kit_with_box, second_kit_with_box):
        """Test 404 error when expendable doesn't exist"""
        from_kit = kit_with_box["kit"]
        to_kit = second_kit_with_box["kit"]
        to_box = second_kit_with_box["box"]

        data = {
            "from_kit_id": from_kit.id,
            "to_kit_id": to_kit.id,
            "to_box_id": to_box.id,
            "expendable_id": 99999
        }

        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json=data,
            headers=auth_headers_materials
        )

        assert response.status_code == 404

    def test_unauthenticated_request(self, client, kit_with_box, second_kit_with_box, expendable_in_kit):
        """Test authentication required for transferring expendables"""
        from_kit = kit_with_box["kit"]
        to_kit = second_kit_with_box["kit"]
        to_box = second_kit_with_box["box"]
        expendable = expendable_in_kit["expendable"]

        data = {
            "from_kit_id": from_kit.id,
            "to_kit_id": to_kit.id,
            "to_box_id": to_box.id,
            "expendable_id": expendable.id
        }

        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json=data
        )

        assert response.status_code == 401

    def test_wrong_department_access(self, client, user_auth_headers, kit_with_box, second_kit_with_box, expendable_in_kit):
        """Test that non-Materials department users are denied access"""
        from_kit = kit_with_box["kit"]
        to_kit = second_kit_with_box["kit"]
        to_box = second_kit_with_box["box"]
        expendable = expendable_in_kit["expendable"]

        data = {
            "from_kit_id": from_kit.id,
            "to_kit_id": to_kit.id,
            "to_box_id": to_box.id,
            "expendable_id": expendable.id
        }

        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json=data,
            headers=user_auth_headers
        )

        assert response.status_code == 403

    def test_audit_log_created_on_transfer(self, client, auth_headers_materials, kit_with_box, second_kit_with_box, expendable_in_kit, db_session):
        """Test that audit log is created when transferring expendable"""
        from_kit = kit_with_box["kit"]
        to_kit = second_kit_with_box["kit"]
        to_box = second_kit_with_box["box"]
        expendable = expendable_in_kit["expendable"]

        # Clear existing transfer audit logs
        AuditLog.query.filter_by(action_type="expendable_transferred_between_kits").delete()
        db_session.commit()

        data = {
            "from_kit_id": from_kit.id,
            "to_kit_id": to_kit.id,
            "to_box_id": to_box.id,
            "expendable_id": expendable.id
        }

        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json=data,
            headers=auth_headers_materials
        )

        assert response.status_code == 200

        audit_log = AuditLog.query.filter_by(action_type="expendable_transferred_between_kits").first()
        assert audit_log is not None
        assert expendable.part_number in audit_log.action_details
        assert from_kit.name in audit_log.action_details
        assert to_kit.name in audit_log.action_details

    def test_empty_json_body(self, client, auth_headers_materials):
        """Test handling of empty JSON body"""
        response = client.post(
            "/api/transfers/kit-to-kit/expendable",
            json={},
            headers=auth_headers_materials
        )

        assert response.status_code == 400
