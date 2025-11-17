"""
Comprehensive tests for utils/transaction_helper.py
Tests all transaction recording functions, error handling, and edge cases.
"""

import pytest
from unittest.mock import patch, MagicMock
from utils.transaction_helper import (
    record_transaction,
    record_tool_checkout,
    record_tool_return,
    record_chemical_issuance,
    record_chemical_return,
    record_kit_item_transfer,
    record_kit_issuance,
    record_inventory_adjustment,
    record_item_receipt,
    validate_serial_number_uniqueness,
    get_item_transactions,
    get_item_detail_with_transactions,
)
from models import db, Tool, Chemical, InventoryTransaction
from models_kits import KitItem, KitExpendable, Kit, KitBox, AircraftType


class TestRecordTransaction:
    """Tests for the record_transaction function"""

    def test_record_transaction_tool_with_auto_detection(self, app, db_session, regular_user):
        """Test recording transaction with auto-detection of lot/serial for tool"""
        # Create a tool with lot and serial numbers
        tool = Tool(
            tool_number="T100",
            serial_number="SN100",
            lot_number="LOT100",
            description="Test Tool",
            condition="Good",
            location="Warehouse A",
            category="Hand Tools",
            status="available"
        )
        db_session.add(tool)
        db_session.commit()

        transaction = record_transaction(
            item_type="tool",
            item_id=tool.id,
            transaction_type="checkout",
            user_id=regular_user.id,
            quantity_change=-1.0,
            location_from="Warehouse A",
            location_to="Field"
        )

        assert transaction is not None
        assert transaction.item_type == "tool"
        assert transaction.item_id == tool.id
        assert transaction.transaction_type == "checkout"
        assert transaction.user_id == regular_user.id
        assert transaction.quantity_change == -1.0
        assert transaction.lot_number == "LOT100"
        assert transaction.serial_number == "SN100"

    def test_record_transaction_chemical_with_auto_detection(self, app, db_session, regular_user):
        """Test recording transaction with auto-detection for chemical"""
        chemical = Chemical(
            part_number="CHEM100",
            lot_number="CHEMLOT100",
            description="Test Chemical",
            manufacturer="Test Mfg",
            quantity=100.0,
            unit="ml",
            location="Storage A",
            category="Solvents",
            status="available"
        )
        db_session.add(chemical)
        db_session.commit()

        transaction = record_transaction(
            item_type="chemical",
            item_id=chemical.id,
            transaction_type="issuance",
            user_id=regular_user.id,
            quantity_change=-10.0
        )

        assert transaction.lot_number == "CHEMLOT100"
        assert transaction.serial_number is None

    def test_record_transaction_expendable_with_auto_detection(self, app, db_session, regular_user):
        """Test recording transaction with auto-detection for expendable"""
        # Create aircraft type first
        aircraft_type = AircraftType(
            name="Q400-EXP1",
            description="Test Aircraft Type"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        # Create kit and box first
        kit = Kit(
            name="Test Kit EXP1",
            aircraft_type_id=aircraft_type.id,
            description="Test Kit",
            status="active",
            created_by=regular_user.id
        )
        db_session.add(kit)
        db_session.flush()

        box = KitBox(
            kit_id=kit.id,
            box_number="Box1",
            box_type="expendable",
            description="Box 1"
        )
        db_session.add(box)
        db_session.flush()

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number="EXP001",
            serial_number="EXPSN001",
            lot_number="EXPLOT001",
            tracking_type="serial",
            description="Test Expendable",
            quantity=10.0,
            unit="pcs",
            status="available"
        )
        db_session.add(expendable)
        db_session.commit()

        transaction = record_transaction(
            item_type="expendable",
            item_id=expendable.id,
            transaction_type="issuance",
            user_id=regular_user.id,
            quantity_change=-5.0
        )

        assert transaction.lot_number == "EXPLOT001"
        assert transaction.serial_number == "EXPSN001"

    def test_record_transaction_kit_item_with_auto_detection(self, app, db_session, regular_user):
        """Test recording transaction with auto-detection for kit_item"""
        # Create aircraft type first
        aircraft_type = AircraftType(
            name="Q400-KITITEM1",
            description="Test Aircraft Type"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        # Create kit and box first
        kit = Kit(
            name="Test Kit KITITEM1",
            aircraft_type_id=aircraft_type.id,
            description="Test Kit 2",
            status="active",
            created_by=regular_user.id
        )
        db_session.add(kit)
        db_session.flush()

        box = KitBox(
            kit_id=kit.id,
            box_number="Box1",
            box_type="tooling",
            description="Box 1"
        )
        db_session.add(box)
        db_session.flush()

        kit_item = KitItem(
            kit_id=kit.id,
            box_id=box.id,
            item_type="tool",
            item_id=999,
            part_number="KITPART001",
            serial_number="KITSN001",
            lot_number="KITLOT001",
            description="Kit Tool Item",
            quantity=1.0,
            status="available"
        )
        db_session.add(kit_item)
        db_session.commit()

        transaction = record_transaction(
            item_type="kit_item",
            item_id=kit_item.id,
            transaction_type="transfer",
            user_id=regular_user.id,
            quantity_change=1.0
        )

        assert transaction.lot_number == "KITLOT001"
        assert transaction.serial_number == "KITSN001"

    def test_record_transaction_with_explicit_lot_serial(self, app, db_session, regular_user):
        """Test that explicitly provided lot/serial numbers override auto-detection"""
        tool = Tool(
            tool_number="T200",
            serial_number="SN200",
            lot_number="LOT200",
            description="Test Tool 2",
            condition="Good",
            location="Warehouse B",
            category="Power Tools",
            status="available"
        )
        db_session.add(tool)
        db_session.commit()

        transaction = record_transaction(
            item_type="tool",
            item_id=tool.id,
            transaction_type="transfer",
            user_id=regular_user.id,
            lot_number="CUSTOM_LOT",
            serial_number="CUSTOM_SERIAL"
        )

        assert transaction.lot_number == "CUSTOM_LOT"
        assert transaction.serial_number == "CUSTOM_SERIAL"

    def test_record_transaction_tool_not_found(self, app, db_session, regular_user):
        """Test recording transaction when tool is not found (no auto-detection)"""
        transaction = record_transaction(
            item_type="tool",
            item_id=99999,
            transaction_type="checkout",
            user_id=regular_user.id,
            quantity_change=-1.0
        )

        assert transaction is not None
        assert transaction.lot_number is None
        assert transaction.serial_number is None

    def test_record_transaction_chemical_not_found(self, app, db_session, regular_user):
        """Test recording transaction when chemical is not found"""
        transaction = record_transaction(
            item_type="chemical",
            item_id=99999,
            transaction_type="issuance",
            user_id=regular_user.id,
            quantity_change=-5.0
        )

        assert transaction.lot_number is None

    def test_record_transaction_expendable_not_found(self, app, db_session, regular_user):
        """Test recording transaction when expendable is not found"""
        transaction = record_transaction(
            item_type="expendable",
            item_id=99999,
            transaction_type="issuance",
            user_id=regular_user.id,
            quantity_change=-3.0
        )

        assert transaction.lot_number is None
        assert transaction.serial_number is None

    def test_record_transaction_kit_item_not_found(self, app, db_session, regular_user):
        """Test recording transaction when kit_item is not found"""
        transaction = record_transaction(
            item_type="kit_item",
            item_id=99999,
            transaction_type="transfer",
            user_id=regular_user.id,
            quantity_change=1.0
        )

        assert transaction.lot_number is None
        assert transaction.serial_number is None

    def test_record_transaction_with_all_kwargs(self, app, db_session, regular_user):
        """Test recording transaction with all optional kwargs"""
        transaction = record_transaction(
            item_type="tool",
            item_id=1,
            transaction_type="transfer",
            user_id=regular_user.id,
            quantity_change=1.0,
            location_from="Source",
            location_to="Destination",
            reference_number="REF123",
            notes="Test notes"
        )

        assert transaction.quantity_change == 1.0
        assert transaction.location_from == "Source"
        assert transaction.location_to == "Destination"
        assert transaction.reference_number == "REF123"
        assert transaction.notes == "Test notes"

    def test_record_transaction_error_handling(self, app, db_session, regular_user):
        """Test that errors are properly raised"""
        with patch('utils.transaction_helper.InventoryTransaction.create_transaction') as mock_create:
            mock_create.side_effect = Exception("Database error")

            with pytest.raises(Exception) as excinfo:
                record_transaction(
                    item_type="tool",
                    item_id=1,
                    transaction_type="checkout",
                    user_id=regular_user.id
                )

            assert "Database error" in str(excinfo.value)


class TestRecordToolCheckout:
    """Tests for record_tool_checkout function"""

    def test_record_tool_checkout_basic(self, app, db_session, regular_user, test_tool):
        """Test basic tool checkout recording"""
        transaction = record_tool_checkout(
            tool_id=test_tool.id,
            user_id=regular_user.id
        )

        assert transaction.transaction_type == "checkout"
        assert transaction.quantity_change == -1.0
        assert transaction.location_from == test_tool.location
        assert f"user {regular_user.id}" in transaction.location_to
        assert transaction.reference_number is None

    def test_record_tool_checkout_with_expected_return(self, app, db_session, regular_user, test_tool):
        """Test tool checkout with expected return date"""
        transaction = record_tool_checkout(
            tool_id=test_tool.id,
            user_id=regular_user.id,
            expected_return_date="2025-12-31"
        )

        assert "Expected return: 2025-12-31" in transaction.reference_number

    def test_record_tool_checkout_with_notes(self, app, db_session, regular_user, test_tool):
        """Test tool checkout with notes"""
        transaction = record_tool_checkout(
            tool_id=test_tool.id,
            user_id=regular_user.id,
            notes="For maintenance task"
        )

        assert transaction.notes == "For maintenance task"

    def test_record_tool_checkout_tool_not_found(self, app, db_session, regular_user):
        """Test tool checkout when tool doesn't exist"""
        with pytest.raises(ValueError) as excinfo:
            record_tool_checkout(
                tool_id=99999,
                user_id=regular_user.id
            )

        assert "Tool 99999 not found" in str(excinfo.value)


class TestRecordToolReturn:
    """Tests for record_tool_return function"""

    def test_record_tool_return_basic(self, app, db_session, regular_user, test_tool):
        """Test basic tool return recording"""
        transaction = record_tool_return(
            tool_id=test_tool.id,
            user_id=regular_user.id
        )

        assert transaction.transaction_type == "return"
        assert transaction.quantity_change == 1.0
        assert f"user {regular_user.id}" in transaction.location_from
        assert transaction.location_to == test_tool.location
        assert transaction.notes is None

    def test_record_tool_return_with_condition(self, app, db_session, regular_user, test_tool):
        """Test tool return with condition"""
        transaction = record_tool_return(
            tool_id=test_tool.id,
            user_id=regular_user.id,
            condition="Good"
        )

        assert "Condition: Good" in transaction.notes

    def test_record_tool_return_with_condition_and_notes(self, app, db_session, regular_user, test_tool):
        """Test tool return with condition and notes"""
        transaction = record_tool_return(
            tool_id=test_tool.id,
            user_id=regular_user.id,
            condition="Fair",
            notes="Slight wear noticed"
        )

        assert "Condition: Fair" in transaction.notes
        assert "Slight wear noticed" in transaction.notes

    def test_record_tool_return_with_notes_only(self, app, db_session, regular_user, test_tool):
        """Test tool return with notes only (no condition)"""
        transaction = record_tool_return(
            tool_id=test_tool.id,
            user_id=regular_user.id,
            notes="Returned on time"
        )

        assert transaction.notes == "Returned on time"

    def test_record_tool_return_tool_not_found(self, app, db_session, regular_user):
        """Test tool return when tool doesn't exist"""
        with pytest.raises(ValueError) as excinfo:
            record_tool_return(
                tool_id=99999,
                user_id=regular_user.id
            )

        assert "Tool 99999 not found" in str(excinfo.value)


class TestRecordChemicalIssuance:
    """Tests for record_chemical_issuance function"""

    def test_record_chemical_issuance_basic(self, app, db_session, regular_user, test_chemical):
        """Test basic chemical issuance"""
        transaction = record_chemical_issuance(
            chemical_id=test_chemical.id,
            user_id=regular_user.id,
            quantity=10.0
        )

        assert transaction.transaction_type == "issuance"
        assert transaction.quantity_change == -10.0
        assert transaction.location_from == test_chemical.location
        assert transaction.notes is None

    def test_record_chemical_issuance_with_hangar(self, app, db_session, regular_user, test_chemical):
        """Test chemical issuance with hangar destination"""
        transaction = record_chemical_issuance(
            chemical_id=test_chemical.id,
            user_id=regular_user.id,
            quantity=5.0,
            hangar="Hangar B"
        )

        assert transaction.location_to == "Hangar B"

    def test_record_chemical_issuance_with_purpose(self, app, db_session, regular_user, test_chemical):
        """Test chemical issuance with purpose"""
        transaction = record_chemical_issuance(
            chemical_id=test_chemical.id,
            user_id=regular_user.id,
            quantity=15.0,
            purpose="Cleaning"
        )

        assert "Purpose: Cleaning" in transaction.notes

    def test_record_chemical_issuance_with_work_order(self, app, db_session, regular_user, test_chemical):
        """Test chemical issuance with work order"""
        transaction = record_chemical_issuance(
            chemical_id=test_chemical.id,
            user_id=regular_user.id,
            quantity=20.0,
            work_order="WO12345"
        )

        assert transaction.reference_number == "WO12345"

    def test_record_chemical_issuance_with_recipient(self, app, db_session, regular_user, test_chemical, admin_user):
        """Test chemical issuance with recipient different from user"""
        transaction = record_chemical_issuance(
            chemical_id=test_chemical.id,
            user_id=regular_user.id,
            quantity=25.0,
            recipient_id=admin_user.id
        )

        assert f"Recipient User ID: {admin_user.id}" in transaction.notes

    def test_record_chemical_issuance_with_same_recipient(self, app, db_session, regular_user, test_chemical):
        """Test chemical issuance when recipient is same as user (no recipient note)"""
        transaction = record_chemical_issuance(
            chemical_id=test_chemical.id,
            user_id=regular_user.id,
            quantity=8.0,
            recipient_id=regular_user.id
        )

        # No recipient note when recipient_id equals user_id
        assert transaction.notes is None or "Recipient User ID" not in transaction.notes

    def test_record_chemical_issuance_with_purpose_and_recipient(self, app, db_session, regular_user, test_chemical, admin_user):
        """Test chemical issuance with both purpose and recipient"""
        transaction = record_chemical_issuance(
            chemical_id=test_chemical.id,
            user_id=regular_user.id,
            quantity=30.0,
            purpose="Testing",
            recipient_id=admin_user.id
        )

        assert "Purpose: Testing" in transaction.notes
        assert f"Recipient User ID: {admin_user.id}" in transaction.notes

    def test_record_chemical_issuance_all_params(self, app, db_session, regular_user, test_chemical, admin_user):
        """Test chemical issuance with all parameters"""
        transaction = record_chemical_issuance(
            chemical_id=test_chemical.id,
            user_id=regular_user.id,
            quantity=50.0,
            hangar="Hangar C",
            purpose="Maintenance",
            work_order="WO67890",
            recipient_id=admin_user.id
        )

        assert transaction.location_to == "Hangar C"
        assert transaction.reference_number == "WO67890"
        assert "Purpose: Maintenance" in transaction.notes
        assert f"Recipient User ID: {admin_user.id}" in transaction.notes

    def test_record_chemical_issuance_not_found(self, app, db_session, regular_user):
        """Test chemical issuance when chemical doesn't exist"""
        with pytest.raises(ValueError) as excinfo:
            record_chemical_issuance(
                chemical_id=99999,
                user_id=regular_user.id,
                quantity=10.0
            )

        assert "Chemical 99999 not found" in str(excinfo.value)


class TestRecordChemicalReturn:
    """Tests for record_chemical_return function"""

    def test_record_chemical_return_basic(self, app, db_session, regular_user, test_chemical):
        """Test basic chemical return"""
        transaction = record_chemical_return(
            chemical_id=test_chemical.id,
            user_id=regular_user.id,
            quantity=5.0
        )

        assert transaction.transaction_type == "return"
        assert transaction.quantity_change == 5.0
        assert transaction.location_to == test_chemical.location

    def test_record_chemical_return_with_locations(self, app, db_session, regular_user, test_chemical):
        """Test chemical return with specified locations"""
        transaction = record_chemical_return(
            chemical_id=test_chemical.id,
            user_id=regular_user.id,
            quantity=10.0,
            location_from="Field",
            location_to="Storage B"
        )

        assert transaction.location_from == "Field"
        assert transaction.location_to == "Storage B"

    def test_record_chemical_return_with_notes(self, app, db_session, regular_user, test_chemical):
        """Test chemical return with notes"""
        transaction = record_chemical_return(
            chemical_id=test_chemical.id,
            user_id=regular_user.id,
            quantity=3.0,
            notes="Unused portion returned"
        )

        assert transaction.notes == "Unused portion returned"

    def test_record_chemical_return_not_found(self, app, db_session, regular_user):
        """Test chemical return when chemical doesn't exist"""
        with pytest.raises(ValueError) as excinfo:
            record_chemical_return(
                chemical_id=99999,
                user_id=regular_user.id,
                quantity=5.0
            )

        assert "Chemical 99999 not found" in str(excinfo.value)


class TestRecordKitItemTransfer:
    """Tests for record_kit_item_transfer function"""

    def test_record_kit_item_transfer_basic(self, app, db_session, regular_user):
        """Test basic kit item transfer"""
        transaction = record_kit_item_transfer(
            item_type="kit_item",
            item_id=1,
            user_id=regular_user.id,
            from_location="Location A",
            to_location="Location B"
        )

        assert transaction.transaction_type == "transfer"
        assert transaction.location_from == "Location A"
        assert transaction.location_to == "Location B"

    def test_record_kit_item_transfer_with_quantity(self, app, db_session, regular_user):
        """Test kit item transfer with quantity"""
        transaction = record_kit_item_transfer(
            item_type="expendable",
            item_id=2,
            user_id=regular_user.id,
            from_location="Source",
            to_location="Destination",
            quantity=5.0
        )

        assert transaction.quantity_change == 5.0

    def test_record_kit_item_transfer_with_reference(self, app, db_session, regular_user):
        """Test kit item transfer with reference number"""
        transaction = record_kit_item_transfer(
            item_type="kit_item",
            item_id=3,
            user_id=regular_user.id,
            from_location="Origin",
            to_location="Target",
            reference="TRANSFER123"
        )

        assert transaction.reference_number == "TRANSFER123"

    def test_record_kit_item_transfer_with_notes(self, app, db_session, regular_user):
        """Test kit item transfer with notes"""
        transaction = record_kit_item_transfer(
            item_type="kit_item",
            item_id=4,
            user_id=regular_user.id,
            from_location="From",
            to_location="To",
            notes="Transferred for kit reorganization"
        )

        assert transaction.notes == "Transferred for kit reorganization"


class TestRecordKitIssuance:
    """Tests for record_kit_issuance function"""

    def test_record_kit_issuance_basic(self, app, db_session, regular_user):
        """Test basic kit issuance"""
        transaction = record_kit_issuance(
            item_type="expendable",
            item_id=1,
            user_id=regular_user.id,
            quantity=10.0
        )

        assert transaction.transaction_type == "kit_issuance"
        assert transaction.quantity_change == -10.0

    def test_record_kit_issuance_with_work_order(self, app, db_session, regular_user):
        """Test kit issuance with work order"""
        transaction = record_kit_issuance(
            item_type="kit_item",
            item_id=2,
            user_id=regular_user.id,
            quantity=5.0,
            work_order="WO-KIT-001"
        )

        assert transaction.reference_number == "WO-KIT-001"

    def test_record_kit_issuance_with_purpose(self, app, db_session, regular_user):
        """Test kit issuance with purpose"""
        transaction = record_kit_issuance(
            item_type="expendable",
            item_id=3,
            user_id=regular_user.id,
            quantity=20.0,
            purpose="Scheduled maintenance"
        )

        assert "Purpose: Scheduled maintenance" in transaction.notes

    def test_record_kit_issuance_with_purpose_and_notes(self, app, db_session, regular_user):
        """Test kit issuance with purpose and additional notes"""
        transaction = record_kit_issuance(
            item_type="kit_item",
            item_id=4,
            user_id=regular_user.id,
            quantity=3.0,
            purpose="Repair",
            notes="Critical repair task"
        )

        assert "Purpose: Repair" in transaction.notes
        assert "Critical repair task" in transaction.notes

    def test_record_kit_issuance_with_notes_only(self, app, db_session, regular_user):
        """Test kit issuance with notes but no purpose"""
        transaction = record_kit_issuance(
            item_type="expendable",
            item_id=5,
            user_id=regular_user.id,
            quantity=7.0,
            notes="Standard issuance"
        )

        assert transaction.notes == "Standard issuance"


class TestRecordInventoryAdjustment:
    """Tests for record_inventory_adjustment function"""

    def test_record_inventory_adjustment_positive(self, app, db_session, regular_user):
        """Test positive inventory adjustment"""
        transaction = record_inventory_adjustment(
            item_type="chemical",
            item_id=1,
            user_id=regular_user.id,
            quantity_change=10.0,
            reason="Physical count correction"
        )

        assert transaction.transaction_type == "adjustment"
        assert transaction.quantity_change == 10.0
        assert "Reason: Physical count correction" in transaction.notes

    def test_record_inventory_adjustment_negative(self, app, db_session, regular_user):
        """Test negative inventory adjustment"""
        transaction = record_inventory_adjustment(
            item_type="expendable",
            item_id=2,
            user_id=regular_user.id,
            quantity_change=-5.0,
            reason="Damaged items removed"
        )

        assert transaction.quantity_change == -5.0
        assert "Reason: Damaged items removed" in transaction.notes

    def test_record_inventory_adjustment_with_notes(self, app, db_session, regular_user):
        """Test inventory adjustment with additional notes"""
        transaction = record_inventory_adjustment(
            item_type="tool",
            item_id=3,
            user_id=regular_user.id,
            quantity_change=1.0,
            reason="Miscount",
            notes="Found during audit"
        )

        assert "Reason: Miscount" in transaction.notes
        assert "Found during audit" in transaction.notes

    def test_record_inventory_adjustment_reason_only(self, app, db_session, regular_user):
        """Test inventory adjustment with reason only"""
        transaction = record_inventory_adjustment(
            item_type="chemical",
            item_id=4,
            user_id=regular_user.id,
            quantity_change=-2.0,
            reason="Spillage"
        )

        assert transaction.notes == "Reason: Spillage"


class TestRecordItemReceipt:
    """Tests for record_item_receipt function"""

    def test_record_item_receipt_basic(self, app, db_session, regular_user):
        """Test basic item receipt"""
        transaction = record_item_receipt(
            item_type="tool",
            item_id=1,
            user_id=regular_user.id,
            quantity=1.0,
            location="Warehouse A"
        )

        assert transaction.transaction_type == "receipt"
        assert transaction.quantity_change == 1.0
        assert transaction.location_to == "Warehouse A"

    def test_record_item_receipt_with_po(self, app, db_session, regular_user):
        """Test item receipt with purchase order"""
        transaction = record_item_receipt(
            item_type="chemical",
            item_id=2,
            user_id=regular_user.id,
            quantity=100.0,
            location="Storage Room",
            po_number="PO-2025-001"
        )

        assert transaction.reference_number == "PO-2025-001"

    def test_record_item_receipt_with_notes(self, app, db_session, regular_user):
        """Test item receipt with notes"""
        transaction = record_item_receipt(
            item_type="expendable",
            item_id=3,
            user_id=regular_user.id,
            quantity=50.0,
            location="Receiving Dock",
            notes="New shipment from vendor"
        )

        assert transaction.notes == "New shipment from vendor"

    def test_record_item_receipt_all_params(self, app, db_session, regular_user):
        """Test item receipt with all parameters"""
        transaction = record_item_receipt(
            item_type="kit_item",
            item_id=4,
            user_id=regular_user.id,
            quantity=25.0,
            location="Main Warehouse",
            po_number="PO-2025-002",
            notes="Express delivery"
        )

        assert transaction.location_to == "Main Warehouse"
        assert transaction.reference_number == "PO-2025-002"
        assert transaction.notes == "Express delivery"


class TestValidateSerialNumberUniqueness:
    """Tests for validate_serial_number_uniqueness function"""

    def test_validate_tool_unique_serial(self, app, db_session):
        """Test validation passes for unique tool serial number"""
        tool = Tool(
            tool_number="T300",
            serial_number="SN300",
            description="Existing Tool",
            condition="Good",
            location="Warehouse",
            category="Tools",
            status="available"
        )
        db_session.add(tool)
        db_session.commit()

        is_valid, error = validate_serial_number_uniqueness(
            part_number="T300",
            serial_number="SN301",  # Different serial
            item_type="tool"
        )

        assert is_valid is True
        assert error is None

    def test_validate_tool_duplicate_serial(self, app, db_session):
        """Test validation fails for duplicate tool serial number"""
        tool = Tool(
            tool_number="T400",
            serial_number="SN400",
            description="Existing Tool",
            condition="Good",
            location="Warehouse",
            category="Tools",
            status="available"
        )
        db_session.add(tool)
        db_session.commit()

        is_valid, error = validate_serial_number_uniqueness(
            part_number="T400",
            serial_number="SN400",  # Same serial
            item_type="tool"
        )

        assert is_valid is False
        assert "already exists" in error
        assert "SN400" in error
        assert "T400" in error

    def test_validate_tool_with_exclude_id(self, app, db_session):
        """Test tool validation with exclude_id (for updates)"""
        tool = Tool(
            tool_number="T500",
            serial_number="SN500",
            description="Tool to Update",
            condition="Good",
            location="Warehouse",
            category="Tools",
            status="available"
        )
        db_session.add(tool)
        db_session.commit()

        # Should pass when excluding the same tool's ID
        is_valid, error = validate_serial_number_uniqueness(
            part_number="T500",
            serial_number="SN500",
            item_type="tool",
            exclude_id=tool.id
        )

        assert is_valid is True
        assert error is None

    def test_validate_expendable_unique_serial(self, app, db_session, regular_user):
        """Test validation passes for unique expendable serial number"""
        aircraft_type = AircraftType(
            name="Q400-VAL-UNIQUE",
            description="Test Aircraft Type"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        kit = Kit(
            name="Test Kit VAL-UNIQUE",
            aircraft_type_id=aircraft_type.id,
            description="Test Kit",
            status="active",
            created_by=regular_user.id
        )
        db_session.add(kit)
        db_session.flush()

        box = KitBox(
            kit_id=kit.id,
            box_number="Box1",
            box_type="expendable",
            description="Box 1"
        )
        db_session.add(box)
        db_session.flush()

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number="EXP-PN100",
            serial_number="EXP-SN100",
            tracking_type="serial",
            description="Expendable Item",
            quantity=1.0,
            unit="pcs",
            status="available"
        )
        db_session.add(expendable)
        db_session.commit()

        is_valid, error = validate_serial_number_uniqueness(
            part_number="EXP-PN100",
            serial_number="EXP-SN101",  # Different serial
            item_type="expendable"
        )

        assert is_valid is True
        assert error is None

    def test_validate_expendable_duplicate_serial(self, app, db_session, regular_user):
        """Test validation fails for duplicate expendable serial number"""
        aircraft_type = AircraftType(
            name="Q400-VAL-DUP",
            description="Test Aircraft Type"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        kit = Kit(
            name="Test Kit VAL-DUP",
            aircraft_type_id=aircraft_type.id,
            description="Test Kit 2",
            status="active",
            created_by=regular_user.id
        )
        db_session.add(kit)
        db_session.flush()

        box = KitBox(
            kit_id=kit.id,
            box_number="Box1",
            box_type="expendable",
            description="Box 1"
        )
        db_session.add(box)
        db_session.flush()

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number="EXP-PN200",
            serial_number="EXP-SN200",
            tracking_type="serial",
            description="Expendable Item",
            quantity=1.0,
            unit="pcs",
            status="available"
        )
        db_session.add(expendable)
        db_session.commit()

        is_valid, error = validate_serial_number_uniqueness(
            part_number="EXP-PN200",
            serial_number="EXP-SN200",  # Same serial
            item_type="expendable"
        )

        assert is_valid is False
        assert "already exists" in error
        assert "EXP-SN200" in error
        assert "EXP-PN200" in error

    def test_validate_expendable_with_exclude_id(self, app, db_session, regular_user):
        """Test expendable validation with exclude_id"""
        aircraft_type = AircraftType(
            name="Q400-VAL-EXCL",
            description="Test Aircraft Type"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        kit = Kit(
            name="Test Kit VAL-EXCL",
            aircraft_type_id=aircraft_type.id,
            description="Test Kit 3",
            status="active",
            created_by=regular_user.id
        )
        db_session.add(kit)
        db_session.flush()

        box = KitBox(
            kit_id=kit.id,
            box_number="Box1",
            box_type="expendable",
            description="Box 1"
        )
        db_session.add(box)
        db_session.flush()

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number="EXP-PN300",
            serial_number="EXP-SN300",
            tracking_type="serial",
            description="Expendable Item",
            quantity=1.0,
            unit="pcs",
            status="available"
        )
        db_session.add(expendable)
        db_session.commit()

        is_valid, error = validate_serial_number_uniqueness(
            part_number="EXP-PN300",
            serial_number="EXP-SN300",
            item_type="expendable",
            exclude_id=expendable.id
        )

        assert is_valid is True
        assert error is None

    def test_validate_no_serial_number(self, app, db_session):
        """Test validation passes when no serial number provided"""
        is_valid, error = validate_serial_number_uniqueness(
            part_number="ANY",
            serial_number=None,
            item_type="tool"
        )

        assert is_valid is True
        assert error is None

    def test_validate_empty_serial_number(self, app, db_session):
        """Test validation passes for empty serial number string"""
        is_valid, error = validate_serial_number_uniqueness(
            part_number="ANY",
            serial_number="",
            item_type="tool"
        )

        assert is_valid is True
        assert error is None

    def test_validate_unknown_item_type(self, app, db_session):
        """Test validation passes for unknown item type (no specific check)"""
        is_valid, error = validate_serial_number_uniqueness(
            part_number="UNKNOWN",
            serial_number="SN999",
            item_type="unknown"
        )

        assert is_valid is True
        assert error is None


class TestGetItemTransactions:
    """Tests for get_item_transactions function"""

    def test_get_item_transactions_empty(self, app, db_session, regular_user):
        """Test getting transactions when none exist"""
        transactions = get_item_transactions(
            item_type="tool",
            item_id=99999
        )

        assert transactions == []

    def test_get_item_transactions_single(self, app, db_session, regular_user, test_tool):
        """Test getting single transaction"""
        record_tool_checkout(
            tool_id=test_tool.id,
            user_id=regular_user.id
        )
        db_session.commit()

        transactions = get_item_transactions(
            item_type="tool",
            item_id=test_tool.id
        )

        assert len(transactions) == 1
        assert transactions[0]["transaction_type"] == "checkout"

    def test_get_item_transactions_multiple(self, app, db_session, regular_user, test_tool):
        """Test getting multiple transactions"""
        record_tool_checkout(test_tool.id, regular_user.id)
        record_tool_return(test_tool.id, regular_user.id)
        record_tool_checkout(test_tool.id, regular_user.id)
        db_session.commit()

        transactions = get_item_transactions(
            item_type="tool",
            item_id=test_tool.id
        )

        assert len(transactions) == 3

    def test_get_item_transactions_with_limit(self, app, db_session, regular_user, test_tool):
        """Test getting transactions with limit"""
        for _ in range(5):
            record_tool_checkout(test_tool.id, regular_user.id)
            record_tool_return(test_tool.id, regular_user.id)
        db_session.commit()

        transactions = get_item_transactions(
            item_type="tool",
            item_id=test_tool.id,
            limit=3
        )

        assert len(transactions) == 3

    def test_get_item_transactions_with_offset(self, app, db_session, regular_user, test_tool):
        """Test getting transactions with offset"""
        for _ in range(5):
            record_tool_checkout(test_tool.id, regular_user.id)
        db_session.commit()

        transactions = get_item_transactions(
            item_type="tool",
            item_id=test_tool.id,
            offset=2
        )

        assert len(transactions) == 3

    def test_get_item_transactions_order(self, app, db_session, regular_user, test_tool):
        """Test that transactions are ordered by timestamp descending"""
        checkout_txn = record_tool_checkout(test_tool.id, regular_user.id)
        db_session.commit()

        return_txn = record_tool_return(test_tool.id, regular_user.id)
        db_session.commit()

        transactions = get_item_transactions(
            item_type="tool",
            item_id=test_tool.id
        )

        # Most recent first (return should be first)
        assert transactions[0]["id"] == return_txn.id
        assert transactions[1]["id"] == checkout_txn.id


class TestGetItemDetailWithTransactions:
    """Tests for get_item_detail_with_transactions function"""

    def test_get_tool_detail_with_transactions(self, app, db_session, regular_user, test_tool):
        """Test getting tool details with transactions"""
        record_tool_checkout(test_tool.id, regular_user.id)
        db_session.commit()

        result = get_item_detail_with_transactions(
            item_type="tool",
            item_id=test_tool.id
        )

        assert result is not None
        assert result["id"] == test_tool.id
        assert result["tool_number"] == test_tool.tool_number
        assert "transactions" in result
        assert result["transaction_count"] == 1

    def test_get_chemical_detail_with_transactions(self, app, db_session, regular_user, test_chemical):
        """Test getting chemical details with transactions"""
        record_chemical_issuance(
            test_chemical.id,
            regular_user.id,
            10.0
        )
        db_session.commit()

        result = get_item_detail_with_transactions(
            item_type="chemical",
            item_id=test_chemical.id
        )

        assert result is not None
        assert result["id"] == test_chemical.id
        assert result["part_number"] == test_chemical.part_number
        assert "transactions" in result
        assert result["transaction_count"] == 1

    def test_get_expendable_detail_with_transactions(self, app, db_session, regular_user):
        """Test getting expendable details with transactions"""
        aircraft_type = AircraftType(
            name="Q400-DET-EXP",
            description="Test Aircraft Type"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        kit = Kit(
            name="Test Kit DET-EXP",
            aircraft_type_id=aircraft_type.id,
            description="Test Kit",
            status="active",
            created_by=regular_user.id
        )
        db_session.add(kit)
        db_session.flush()

        box = KitBox(
            kit_id=kit.id,
            box_number="Box1",
            box_type="expendable",
            description="Box 1"
        )
        db_session.add(box)
        db_session.flush()

        expendable = KitExpendable(
            kit_id=kit.id,
            box_id=box.id,
            part_number="EXP-DET001",
            serial_number="EXP-SN-DET001",
            tracking_type="serial",
            description="Expendable for Detail",
            quantity=10.0,
            unit="pcs",
            status="available"
        )
        db_session.add(expendable)
        db_session.commit()

        record_transaction(
            item_type="expendable",
            item_id=expendable.id,
            transaction_type="issuance",
            user_id=regular_user.id,
            quantity_change=-2.0
        )
        db_session.commit()

        result = get_item_detail_with_transactions(
            item_type="expendable",
            item_id=expendable.id
        )

        assert result is not None
        assert result["id"] == expendable.id
        assert result["part_number"] == expendable.part_number
        assert "transactions" in result
        assert result["transaction_count"] == 1

    def test_get_kit_item_detail_with_transactions(self, app, db_session, regular_user):
        """Test getting kit_item details with transactions"""
        aircraft_type = AircraftType(
            name="Q400-DET-KITITEM",
            description="Test Aircraft Type"
        )
        db_session.add(aircraft_type)
        db_session.flush()

        kit = Kit(
            name="Test Kit DET-KITITEM",
            aircraft_type_id=aircraft_type.id,
            description="Test Kit",
            status="active",
            created_by=regular_user.id
        )
        db_session.add(kit)
        db_session.flush()

        box = KitBox(
            kit_id=kit.id,
            box_number="Box1",
            box_type="tooling",
            description="Box 1"
        )
        db_session.add(box)
        db_session.flush()

        kit_item = KitItem(
            kit_id=kit.id,
            box_id=box.id,
            item_type="tool",
            item_id=888,
            part_number="KIT-PART-DET001",
            serial_number="KIT-SN-DET001",
            description="Kit Item for Detail",
            quantity=1.0,
            status="available"
        )
        db_session.add(kit_item)
        db_session.commit()

        record_transaction(
            item_type="kit_item",
            item_id=kit_item.id,
            transaction_type="transfer",
            user_id=regular_user.id,
            quantity_change=1.0
        )
        db_session.commit()

        result = get_item_detail_with_transactions(
            item_type="kit_item",
            item_id=kit_item.id
        )

        assert result is not None
        assert result["id"] == kit_item.id
        assert result["part_number"] == kit_item.part_number
        assert "transactions" in result
        assert result["transaction_count"] == 1

    def test_get_item_detail_not_found(self, app, db_session):
        """Test getting details for non-existent item"""
        result = get_item_detail_with_transactions(
            item_type="tool",
            item_id=99999
        )

        assert result is None

    def test_get_item_detail_unknown_type(self, app, db_session):
        """Test getting details for unknown item type"""
        result = get_item_detail_with_transactions(
            item_type="unknown_type",
            item_id=1
        )

        assert result is None

    def test_get_item_detail_no_transactions(self, app, db_session, test_tool):
        """Test getting item details when no transactions exist"""
        result = get_item_detail_with_transactions(
            item_type="tool",
            item_id=test_tool.id
        )

        assert result is not None
        assert result["transactions"] == []
        assert result["transaction_count"] == 0
