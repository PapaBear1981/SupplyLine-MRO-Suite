"""
Tests for the unified request system.

This module tests that chemical reorders, kit reorders, and manual requests
all create entries in the unified UserRequest system.
"""

import os
import sys
from datetime import datetime, timedelta

import pytest


# Add backend directory to Python path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


@pytest.fixture
def unified_setup(app):
    """Set up test data for unified requests testing."""
    from models import (
        Chemical,
        RequestItem,
        User,
        UserRequest,
        Warehouse,
        db,
    )
    from models_kits import Kit, KitReorderRequest

    with app.app_context():
        db.create_all()

        # Create test user
        user = User(
            employee_number="TEST001",
            name="Test User",
            department="Materials",
            is_admin=True,
            is_active=True,
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.flush()

        # Create a warehouse
        warehouse = Warehouse(
            name="Main Warehouse",
            location="Building A",
            is_active=True,
            warehouse_type="main",
        )
        db.session.add(warehouse)
        db.session.flush()

        # Create a test chemical
        chemical = Chemical(
            part_number="CHEM-001",
            lot_number="LOT-2024-001",
            description="Test Chemical",
            manufacturer="Test Mfg",
            quantity=10,
            unit="mL",
            minimum_stock_level=5,
            status="available",
            warehouse_id=warehouse.id,
            expiration_date=datetime.utcnow() + timedelta(days=365),
        )
        db.session.add(chemical)
        db.session.flush()

        # Create a test kit
        kit = Kit(
            name="Test Kit",
            description="A test kit",
            status="active",
            created_by=user.id,
        )
        db.session.add(kit)
        db.session.flush()

        db.session.commit()

        yield {
            "user": user,
            "warehouse": warehouse,
            "chemical": chemical,
            "kit": kit,
        }


class TestUnifiedRequestHelpers:
    """Test the unified request helper functions."""

    def test_create_chemical_reorder_request(self, app, unified_setup):
        """Test that creating a chemical reorder creates a UserRequest."""
        from models import RequestItem, UserRequest, db
        from utils.unified_requests import create_chemical_reorder_request

        with app.app_context():
            chemical = unified_setup["chemical"]
            user = unified_setup["user"]

            # Create a chemical reorder request
            user_request = create_chemical_reorder_request(
                chemical=chemical,
                requested_quantity=20,
                requester_id=user.id,
                notes="Low stock - need reorder",
            )
            db.session.commit()

            # Verify UserRequest was created
            assert user_request is not None
            assert user_request.id is not None
            assert user_request.request_number is not None
            assert user_request.request_number.startswith("REQ-")
            assert user_request.title.startswith("Chemical Reorder:")
            assert "CHEM-001" in user_request.title
            assert user_request.requester_id == user.id
            assert user_request.priority in ["normal", "high", "critical"]
            assert user_request.status == "new"

            # Verify RequestItem was created
            items = user_request.items.all()
            assert len(items) == 1

            item = items[0]
            assert item.source_type == "chemical_reorder"
            assert item.chemical_id == chemical.id
            assert item.item_type == "chemical"
            assert item.part_number == "CHEM-001"
            assert item.quantity == 20
            assert item.unit == "mL"
            assert item.status == "pending"

    def test_create_kit_reorder_request(self, app, unified_setup):
        """Test that creating a kit reorder creates a UserRequest."""
        from models import RequestItem, UserRequest, db
        from models_kits import KitReorderRequest
        from utils.unified_requests import create_kit_reorder_request

        with app.app_context():
            kit = unified_setup["kit"]
            user = unified_setup["user"]

            # Create a KitReorderRequest
            kit_reorder = KitReorderRequest(
                kit_id=kit.id,
                item_type="expendable",
                part_number="EXP-001",
                description="Test Expendable",
                quantity_requested=10,
                priority="high",
                requested_by=user.id,
                status="pending",
                notes="Urgent need",
            )
            db.session.add(kit_reorder)
            db.session.flush()

            # Create a unified request for the kit reorder
            user_request = create_kit_reorder_request(
                kit=kit,
                reorder_request=kit_reorder,
                requester_id=user.id,
            )
            db.session.commit()

            # Verify UserRequest was created
            assert user_request is not None
            assert user_request.id is not None
            assert user_request.request_number is not None
            assert user_request.request_number.startswith("REQ-")
            assert user_request.title.startswith("Kit Reorder:")
            assert "EXP-001" in user_request.title
            assert user_request.requester_id == user.id
            assert user_request.priority == "high"  # Maps from kit's "high"
            assert user_request.status == "new"

            # Verify RequestItem was created
            items = user_request.items.all()
            assert len(items) == 1

            item = items[0]
            assert item.source_type == "kit_reorder"
            assert item.kit_id == kit.id
            assert item.kit_reorder_request_id == kit_reorder.id
            assert item.item_type == "expendable"
            assert item.part_number == "EXP-001"
            assert item.quantity == 10
            assert item.status == "pending"

    def test_update_request_item_status_chemical(self, app, unified_setup):
        """Test updating request item status for chemical reorders."""
        from models import db
        from utils.unified_requests import (
            create_chemical_reorder_request,
            update_request_item_status,
        )

        with app.app_context():
            chemical = unified_setup["chemical"]
            user = unified_setup["user"]

            # Create a chemical reorder request
            user_request = create_chemical_reorder_request(
                chemical=chemical,
                requested_quantity=20,
                requester_id=user.id,
            )
            db.session.commit()

            # Update the item status to ordered
            item = update_request_item_status(
                source_type="chemical_reorder",
                source_id=chemical.id,
                new_status="ordered",
                vendor="Test Vendor",
                ordered_date=datetime.utcnow(),
            )
            db.session.commit()

            # Verify update
            assert item is not None
            assert item.status == "ordered"
            assert item.vendor == "Test Vendor"
            assert item.ordered_date is not None

            # Verify parent request status updated
            assert user_request.status == "ordered"

    def test_update_request_item_status_kit(self, app, unified_setup):
        """Test updating request item status for kit reorders."""
        from models import db
        from models_kits import KitReorderRequest
        from utils.unified_requests import (
            create_kit_reorder_request,
            update_request_item_status,
        )

        with app.app_context():
            kit = unified_setup["kit"]
            user = unified_setup["user"]

            # Create a KitReorderRequest
            kit_reorder = KitReorderRequest(
                kit_id=kit.id,
                item_type="expendable",
                part_number="EXP-002",
                description="Test Expendable 2",
                quantity_requested=5,
                priority="medium",
                requested_by=user.id,
                status="pending",
            )
            db.session.add(kit_reorder)
            db.session.flush()

            # Create a unified request
            user_request = create_kit_reorder_request(
                kit=kit,
                reorder_request=kit_reorder,
                requester_id=user.id,
            )
            db.session.commit()

            # Update the item status to received
            item = update_request_item_status(
                source_type="kit_reorder",
                source_id=kit_reorder.id,
                new_status="received",
                received_date=datetime.utcnow(),
                received_quantity=5,
            )
            db.session.commit()

            # Verify update
            assert item is not None
            assert item.status == "received"
            assert item.received_date is not None
            assert item.received_quantity == 5

            # Verify parent request status updated
            assert user_request.status == "received"

    def test_chemical_priority_based_on_stock(self, app, unified_setup):
        """Test that chemical reorder priority is based on stock status."""
        from models import db
        from utils.unified_requests import create_chemical_reorder_request

        with app.app_context():
            chemical = unified_setup["chemical"]
            user = unified_setup["user"]

            # Test normal priority (quantity > 0, not expired)
            user_request = create_chemical_reorder_request(
                chemical=chemical,
                requested_quantity=20,
                requester_id=user.id,
            )
            assert user_request.priority == "normal"
            db.session.rollback()

            # Test high priority (quantity = 0)
            chemical.quantity = 0
            user_request = create_chemical_reorder_request(
                chemical=chemical,
                requested_quantity=20,
                requester_id=user.id,
            )
            assert user_request.priority == "high"
            db.session.rollback()

            # Test critical priority (expired)
            chemical.quantity = 10
            chemical.expiration_date = datetime.utcnow() - timedelta(days=1)
            user_request = create_chemical_reorder_request(
                chemical=chemical,
                requested_quantity=20,
                requester_id=user.id,
            )
            assert user_request.priority == "critical"

    def test_request_number_generation(self, app, unified_setup):
        """Test that request numbers are generated uniquely."""
        from models import db
        from utils.unified_requests import create_chemical_reorder_request

        with app.app_context():
            chemical = unified_setup["chemical"]
            user = unified_setup["user"]

            # Create multiple requests
            request1 = create_chemical_reorder_request(
                chemical=chemical,
                requested_quantity=10,
                requester_id=user.id,
            )
            db.session.flush()

            request2 = create_chemical_reorder_request(
                chemical=chemical,
                requested_quantity=20,
                requester_id=user.id,
            )
            db.session.flush()

            # Verify unique request numbers
            assert request1.request_number != request2.request_number
            assert request1.request_number.startswith("REQ-")
            assert request2.request_number.startswith("REQ-")

            # Extract numbers and verify sequence
            num1 = int(request1.request_number.replace("REQ-", ""))
            num2 = int(request2.request_number.replace("REQ-", ""))
            assert num2 == num1 + 1


class TestRequestItemSourceTracking:
    """Test source tracking in RequestItem model."""

    def test_request_item_to_dict_includes_source_fields(self, app, unified_setup):
        """Test that RequestItem.to_dict() includes source tracking fields."""
        from models import db
        from utils.unified_requests import create_chemical_reorder_request

        with app.app_context():
            chemical = unified_setup["chemical"]
            user = unified_setup["user"]

            user_request = create_chemical_reorder_request(
                chemical=chemical,
                requested_quantity=20,
                requester_id=user.id,
            )
            db.session.commit()

            item = user_request.items.first()
            item_dict = item.to_dict()

            # Verify source fields are in the dict
            assert "source_type" in item_dict
            assert "chemical_id" in item_dict
            assert "kit_id" in item_dict
            assert "kit_reorder_request_id" in item_dict

            # Verify values
            assert item_dict["source_type"] == "chemical_reorder"
            assert item_dict["chemical_id"] == chemical.id
            assert item_dict["kit_id"] is None
            assert item_dict["kit_reorder_request_id"] is None

    def test_manual_request_has_manual_source_type(self, app, unified_setup):
        """Test that manually created RequestItems have 'manual' source type."""
        from models import RequestItem, UserRequest, db, get_current_time

        with app.app_context():
            user = unified_setup["user"]

            # Create a manual request
            user_request = UserRequest(
                title="Manual Tool Request",
                description="Need a wrench",
                priority="normal",
                status="new",
                requester_id=user.id,
            )
            db.session.add(user_request)
            db.session.flush()

            # Create a manual item (default source_type)
            item = RequestItem(
                request_id=user_request.id,
                item_type="tool",
                part_number="TOOL-001",
                description="Wrench",
                quantity=1,
                unit="each",
            )
            db.session.add(item)
            db.session.commit()

            # Verify default source_type
            assert item.source_type == "manual"
            assert item.chemical_id is None
            assert item.kit_id is None
            assert item.kit_reorder_request_id is None
