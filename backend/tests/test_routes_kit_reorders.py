"""
Unit tests for Kit Reorder Request API endpoints

Tests all reorder-related API endpoints including:
- Creating reorder requests (manual and automatic)
- Listing reorder requests with filters
- Getting reorder request details
- Approving reorder requests
- Marking reorders as ordered
- Fulfilling reorder requests
- Cancelling reorder requests
- Updating reorder requests
- Authentication and authorization
- Validation and error handling
- Priority handling
"""

import json

import pytest

from models import User
from models_kits import AircraftType, Kit, KitBox, KitExpendable, KitReorderRequest


@pytest.fixture
def aircraft_type(db_session):
    """Create a test aircraft type"""
    aircraft_type = AircraftType.query.filter_by(name="Q400").first()
    if not aircraft_type:
        aircraft_type = AircraftType(name="Q400", description="Test Aircraft", is_active=True)
        db_session.add(aircraft_type)
        db_session.commit()
    return aircraft_type


@pytest.fixture
def test_kit(db_session, admin_user, aircraft_type):
    """Create a test kit"""
    import uuid
    kit_name = f"Test Kit {uuid.uuid4().hex[:8]}"
    kit = Kit(
        name=kit_name,
        aircraft_type_id=aircraft_type.id,
        description="Test kit for reorder tests",
        status="active",
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
        box_number="1",
        box_type="expendable",
        description="Expendable items box"
    )
    db_session.add(box)
    db_session.commit()
    return box


@pytest.fixture
def test_expendable(db_session, test_kit, test_kit_box):
    """Create a test expendable"""
    expendable = KitExpendable(
        kit_id=test_kit.id,
        box_id=test_kit_box.id,
        part_number="EXP-001",
        description="Safety Wire",
        quantity=50.0,
        unit="ft",
        minimum_stock_level=100.0,
        status="available"
    )
    db_session.add(expendable)
    db_session.commit()
    return expendable


@pytest.fixture
def materials_user(db_session):
    """Create a Materials department user"""
    import uuid
    emp_number = f"MAT{uuid.uuid4().hex[:6]}"

    user = User(
        name="Materials User",
        employee_number=emp_number,
        department="Materials",
        is_admin=False,
        is_active=True
    )
    user.set_password("materials123")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def auth_headers_materials(client, materials_user, jwt_manager):
    """Get auth headers for Materials user"""
    with client.application.app_context():
        tokens = jwt_manager.generate_tokens(materials_user)
    access_token = tokens["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def pending_reorder(db_session, test_kit, test_expendable, admin_user):
    """Create a pending reorder request"""
    reorder = KitReorderRequest(
        kit_id=test_kit.id,
        item_type="expendable",
        item_id=test_expendable.id,
        part_number="EXP-001",
        description="Safety Wire",
        quantity_requested=100.0,
        priority="high",
        requested_by=admin_user.id,
        status="pending",
        notes="Low stock - urgent reorder needed",
        is_automatic=False
    )
    db_session.add(reorder)
    db_session.commit()
    return reorder


@pytest.fixture
def approved_reorder(db_session, test_kit, test_expendable, admin_user, materials_user):
    """Create an approved reorder request"""
    from datetime import datetime
    reorder = KitReorderRequest(
        kit_id=test_kit.id,
        item_type="expendable",
        item_id=test_expendable.id,
        part_number="EXP-002",
        description="Lockwire",
        quantity_requested=50.0,
        priority="medium",
        requested_by=admin_user.id,
        status="approved",
        approved_by=materials_user.id,
        approved_date=datetime.now(),
        is_automatic=False
    )
    db_session.add(reorder)
    db_session.commit()
    return reorder


@pytest.fixture
def ordered_reorder(db_session, test_kit, test_expendable, admin_user):
    """Create an ordered reorder request"""
    reorder = KitReorderRequest(
        kit_id=test_kit.id,
        item_type="expendable",
        item_id=test_expendable.id,
        part_number="EXP-003",
        description="Rivets",
        quantity_requested=200.0,
        priority="low",
        requested_by=admin_user.id,
        status="ordered",
        is_automatic=True
    )
    db_session.add(reorder)
    db_session.commit()
    return reorder


class TestCreateReorderRequest:
    """Test creating reorder requests"""

    def test_create_reorder_request_authenticated_user(self, client, auth_headers_user, test_kit):
        """Test creating reorder request as authenticated user"""
        reorder_data = {
            "part_number": "EXP-100",
            "description": "Test Expendable",
            "quantity_requested": 50.0,
            "priority": "medium",
            "notes": "Test reorder request"
        }

        response = client.post(f"/api/kits/{test_kit.id}/reorder",
                             json=reorder_data,
                             headers=auth_headers_user)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data["part_number"] == "EXP-100"
        assert data["description"] == "Test Expendable"
        assert data["quantity_requested"] == 50.0
        assert data["priority"] == "medium"
        assert data["status"] == "pending"
        assert data["is_automatic"] is False

    def test_create_reorder_request_with_item_id(self, client, auth_headers_user, test_kit, test_expendable):
        """Test creating reorder request with item_id"""
        reorder_data = {
            "item_type": "expendable",
            "item_id": test_expendable.id,
            "part_number": "EXP-001",
            "description": "Safety Wire",
            "quantity_requested": 100.0,
            "priority": "high"
        }

        response = client.post(f"/api/kits/{test_kit.id}/reorder",
                             json=reorder_data,
                             headers=auth_headers_user)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data["item_id"] == test_expendable.id
        assert data["item_type"] == "expendable"

    def test_create_reorder_request_missing_part_number(self, client, auth_headers_user, test_kit):
        """Test creating reorder request without part number"""
        reorder_data = {
            "description": "Test Expendable",
            "quantity_requested": 50.0
        }

        response = client.post(f"/api/kits/{test_kit.id}/reorder",
                             json=reorder_data,
                             headers=auth_headers_user)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Part number is required" in data["error"]

    def test_create_reorder_request_missing_description(self, client, auth_headers_user, test_kit):
        """Test creating reorder request without description"""
        reorder_data = {
            "part_number": "EXP-100",
            "quantity_requested": 50.0
        }

        response = client.post(f"/api/kits/{test_kit.id}/reorder",
                             json=reorder_data,
                             headers=auth_headers_user)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Description is required" in data["error"]

    def test_create_reorder_request_missing_quantity(self, client, auth_headers_user, test_kit):
        """Test creating reorder request without quantity"""
        reorder_data = {
            "part_number": "EXP-100",
            "description": "Test Expendable"
        }

        response = client.post(f"/api/kits/{test_kit.id}/reorder",
                             json=reorder_data,
                             headers=auth_headers_user)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Quantity requested is required" in data["error"]

    def test_create_reorder_request_kit_not_found(self, client, auth_headers_user):
        """Test creating reorder request for non-existent kit"""
        reorder_data = {
            "part_number": "EXP-100",
            "description": "Test Expendable",
            "quantity_requested": 50.0
        }

        response = client.post("/api/kits/99999/reorder",
                             json=reorder_data,
                             headers=auth_headers_user)

        assert response.status_code == 404

    def test_create_reorder_request_unauthenticated(self, client, test_kit):
        """Test creating reorder request without authentication"""
        reorder_data = {
            "part_number": "EXP-100",
            "description": "Test Expendable",
            "quantity_requested": 50.0
        }

        response = client.post(f"/api/kits/{test_kit.id}/reorder", json=reorder_data)

        assert response.status_code == 401


class TestGetReorderRequests:
    """Test listing reorder requests"""

    def test_get_all_reorder_requests(self, client, auth_headers_user, pending_reorder):
        """Test getting all reorder requests"""
        response = client.get("/api/reorder-requests", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_reorder_requests_filter_by_kit(self, client, auth_headers_user, pending_reorder, test_kit):
        """Test filtering reorder requests by kit"""
        response = client.get(f"/api/reorder-requests?kit_id={test_kit.id}", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        for reorder in data:
            assert reorder["kit_id"] == test_kit.id

    def test_get_reorder_requests_filter_by_status(self, client, auth_headers_user, pending_reorder):
        """Test filtering reorder requests by status"""
        response = client.get("/api/reorder-requests?status=pending", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        for reorder in data:
            assert reorder["status"] == "pending"

    def test_get_reorder_requests_filter_by_priority(self, client, auth_headers_user, pending_reorder):
        """Test filtering reorder requests by priority"""
        response = client.get("/api/reorder-requests?priority=high", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        for reorder in data:
            assert reorder["priority"] == "high"

    def test_get_reorder_requests_filter_by_is_automatic(self, client, auth_headers_user, pending_reorder, ordered_reorder):
        """Test filtering reorder requests by is_automatic"""
        response = client.get("/api/reorder-requests?is_automatic=true", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        for reorder in data:
            assert reorder["is_automatic"] is True

    def test_get_reorder_requests_unauthenticated(self, client):
        """Test getting reorder requests without authentication"""
        response = client.get("/api/reorder-requests")

        assert response.status_code == 401


class TestGetReorderRequestById:
    """Test getting reorder request details"""

    def test_get_reorder_request_by_id(self, client, auth_headers_user, pending_reorder):
        """Test getting specific reorder request by ID"""
        response = client.get(f"/api/reorder-requests/{pending_reorder.id}", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["id"] == pending_reorder.id
        assert data["status"] == "pending"
        assert "part_number" in data
        assert "quantity_requested" in data

    def test_get_reorder_request_not_found(self, client, auth_headers_user):
        """Test getting non-existent reorder request"""
        response = client.get("/api/reorder-requests/99999", headers=auth_headers_user)

        assert response.status_code == 404

    def test_get_reorder_request_unauthenticated(self, client, pending_reorder):
        """Test getting reorder request without authentication"""
        response = client.get(f"/api/reorder-requests/{pending_reorder.id}")

        assert response.status_code == 401


class TestApproveReorderRequest:
    """Test approving reorder requests"""

    def test_approve_reorder_request_materials_user(self, client, auth_headers_materials, pending_reorder):
        """Test approving reorder request as Materials user"""
        response = client.put(f"/api/reorder-requests/{pending_reorder.id}/approve",
                            headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["status"] == "approved"
        assert data["approved_by"] is not None
        assert data["approved_date"] is not None

    def test_approve_reorder_request_regular_user_forbidden(self, client, auth_headers_user, pending_reorder):
        """Test approving reorder request as regular user (should fail)"""
        response = client.put(f"/api/reorder-requests/{pending_reorder.id}/approve",
                            headers=auth_headers_user)

        assert response.status_code == 403

    def test_approve_reorder_request_not_pending(self, client, auth_headers_materials, approved_reorder):
        """Test approving reorder request that is not pending"""
        response = client.put(f"/api/reorder-requests/{approved_reorder.id}/approve",
                            headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Can only approve pending requests" in data["error"]

    def test_approve_reorder_request_not_found(self, client, auth_headers_materials):
        """Test approving non-existent reorder request"""
        response = client.put("/api/reorder-requests/99999/approve",
                            headers=auth_headers_materials)

        assert response.status_code == 404

    def test_approve_reorder_request_unauthenticated(self, client, pending_reorder):
        """Test approving reorder request without authentication"""
        response = client.put(f"/api/reorder-requests/{pending_reorder.id}/approve")

        assert response.status_code == 401


class TestMarkReorderOrdered:
    """Test marking reorder requests as ordered"""

    def test_mark_reorder_ordered_from_pending(self, client, auth_headers_materials, pending_reorder):
        """Test marking pending reorder as ordered"""
        response = client.put(f"/api/reorder-requests/{pending_reorder.id}/order",
                            headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["status"] == "ordered"

    def test_mark_reorder_ordered_from_approved(self, client, auth_headers_materials, approved_reorder):
        """Test marking approved reorder as ordered"""
        response = client.put(f"/api/reorder-requests/{approved_reorder.id}/order",
                            headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["status"] == "ordered"

    def test_mark_reorder_ordered_regular_user_forbidden(self, client, auth_headers_user, pending_reorder):
        """Test marking reorder as ordered as regular user (should fail)"""
        response = client.put(f"/api/reorder-requests/{pending_reorder.id}/order",
                            headers=auth_headers_user)

        assert response.status_code == 403

    def test_mark_reorder_ordered_invalid_status(self, client, auth_headers_materials, ordered_reorder):
        """Test marking already ordered reorder as ordered"""
        response = client.put(f"/api/reorder-requests/{ordered_reorder.id}/order",
                            headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Can only mark pending or approved requests as ordered" in data["error"]

    def test_mark_reorder_ordered_unauthenticated(self, client, pending_reorder):
        """Test marking reorder as ordered without authentication"""
        response = client.put(f"/api/reorder-requests/{pending_reorder.id}/order")

        assert response.status_code == 401


class TestFulfillReorderRequest:
    """Test fulfilling reorder requests"""

    def test_fulfill_reorder_request_materials_user(self, client, auth_headers_materials, ordered_reorder, test_expendable):
        """Test fulfilling reorder request as Materials user"""
        original_quantity = test_expendable.quantity

        response = client.put(f"/api/reorder-requests/{ordered_reorder.id}/fulfill",
                            headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["status"] == "fulfilled"
        assert data["fulfillment_date"] is not None

        # Verify item quantity was increased
        from models_kits import KitExpendable
        updated_item = KitExpendable.query.get(test_expendable.id)
        assert updated_item.quantity == original_quantity + ordered_reorder.quantity_requested

    def test_fulfill_reorder_request_regular_user_forbidden(self, client, auth_headers_user, ordered_reorder):
        """Test fulfilling reorder request as regular user (should fail)"""
        response = client.put(f"/api/reorder-requests/{ordered_reorder.id}/fulfill",
                            headers=auth_headers_user)

        assert response.status_code == 403

    def test_fulfill_reorder_request_not_ordered(self, client, auth_headers_materials, pending_reorder):
        """Test fulfilling reorder request that is not ordered"""
        response = client.put(f"/api/reorder-requests/{pending_reorder.id}/fulfill",
                            headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Can only fulfill ordered requests" in data["error"]

    def test_fulfill_reorder_request_not_found(self, client, auth_headers_materials):
        """Test fulfilling non-existent reorder request"""
        response = client.put("/api/reorder-requests/99999/fulfill",
                            headers=auth_headers_materials)

        assert response.status_code == 404

    def test_fulfill_reorder_request_unauthenticated(self, client, ordered_reorder):
        """Test fulfilling reorder request without authentication"""
        response = client.put(f"/api/reorder-requests/{ordered_reorder.id}/fulfill")

        assert response.status_code == 401

    def test_fulfill_reorder_request_zero_quantity(self, client, auth_headers_materials, db_session, test_kit, test_expendable, admin_user):
        """Test fulfilling reorder request with zero quantity (should fail)"""
        reorder = KitReorderRequest(
            kit_id=test_kit.id,
            item_type="expendable",
            item_id=test_expendable.id,
            part_number="EXP-ZERO",
            description="Zero Quantity Test",
            quantity_requested=0.0,
            priority="medium",
            requested_by=admin_user.id,
            status="ordered"
        )
        db_session.add(reorder)
        db_session.commit()

        response = client.put(f"/api/reorder-requests/{reorder.id}/fulfill",
                            headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Quantity requested must be greater than zero" in data["error"]

    def test_fulfill_reorder_request_negative_quantity(self, client, auth_headers_materials, db_session, test_kit, test_expendable, admin_user):
        """Test fulfilling reorder request with negative quantity (should fail)"""
        reorder = KitReorderRequest(
            kit_id=test_kit.id,
            item_type="expendable",
            item_id=test_expendable.id,
            part_number="EXP-NEG",
            description="Negative Quantity Test",
            quantity_requested=-10.0,
            priority="medium",
            requested_by=admin_user.id,
            status="ordered"
        )
        db_session.add(reorder)
        db_session.commit()

        response = client.put(f"/api/reorder-requests/{reorder.id}/fulfill",
                            headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Quantity requested must be greater than zero" in data["error"]

    def test_fulfill_tool_reorder_with_quantity_not_one(self, client, auth_headers_materials, db_session, test_kit, admin_user):
        """Test fulfilling tool reorder request with quantity != 1 (should fail)"""
        reorder = KitReorderRequest(
            kit_id=test_kit.id,
            item_type="tool",
            item_id=None,
            part_number="TOOL-001",
            description="Test Tool",
            quantity_requested=5.0,
            priority="medium",
            requested_by=admin_user.id,
            status="ordered"
        )
        db_session.add(reorder)
        db_session.commit()

        response = client.put(f"/api/reorder-requests/{reorder.id}/fulfill",
                            headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Tool quantity must be 1" in data["error"]


class TestCancelReorderRequest:
    """Test cancelling reorder requests"""

    def test_cancel_reorder_request_by_requester(self, client, auth_headers_admin, pending_reorder):
        """Test cancelling reorder request by the requester"""
        response = client.put(f"/api/reorder-requests/{pending_reorder.id}/cancel",
                            headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["status"] == "cancelled"

    def test_cancel_reorder_request_by_materials_user(self, client, auth_headers_materials, pending_reorder):
        """Test cancelling reorder request by Materials user"""
        response = client.put(f"/api/reorder-requests/{pending_reorder.id}/cancel",
                            headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["status"] == "cancelled"

    def test_cancel_reorder_request_unauthorized_user(self, client, auth_headers_user, pending_reorder):
        """Test cancelling reorder request by unauthorized user"""
        response = client.put(f"/api/reorder-requests/{pending_reorder.id}/cancel",
                            headers=auth_headers_user)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "You do not have permission to cancel this request" in data["error"]

    def test_cancel_reorder_request_already_fulfilled(self, client, auth_headers_materials, db_session, test_kit, test_expendable, admin_user):
        """Test cancelling already fulfilled reorder request"""
        from datetime import datetime
        reorder = KitReorderRequest(
            kit_id=test_kit.id,
            item_type="expendable",
            item_id=test_expendable.id,
            part_number="EXP-999",
            description="Test Item",
            quantity_requested=10.0,
            priority="low",
            requested_by=admin_user.id,
            status="fulfilled",
            fulfillment_date=datetime.now()
        )
        db_session.add(reorder)
        db_session.commit()

        response = client.put(f"/api/reorder-requests/{reorder.id}/cancel",
                            headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Cannot cancel fulfilled or already cancelled requests" in data["error"]

    def test_cancel_reorder_request_not_found(self, client, auth_headers_materials):
        """Test cancelling non-existent reorder request"""
        response = client.put("/api/reorder-requests/99999/cancel",
                            headers=auth_headers_materials)

        assert response.status_code == 404

    def test_cancel_reorder_request_unauthenticated(self, client, pending_reorder):
        """Test cancelling reorder request without authentication"""
        response = client.put(f"/api/reorder-requests/{pending_reorder.id}/cancel")

        assert response.status_code == 401


class TestUpdateReorderRequest:
    """Test updating reorder requests"""

    def test_update_reorder_request_by_requester(self, client, auth_headers_admin, pending_reorder):
        """Test updating reorder request by the requester"""
        update_data = {
            "quantity_requested": 150.0,
            "priority": "urgent",
            "notes": "Updated notes"
        }

        response = client.put(f"/api/reorder-requests/{pending_reorder.id}",
                            json=update_data,
                            headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["quantity_requested"] == 150.0
        assert data["priority"] == "urgent"
        assert data["notes"] == "Updated notes"

    def test_update_reorder_request_by_materials_user(self, client, auth_headers_materials, pending_reorder):
        """Test updating reorder request by Materials user"""
        update_data = {
            "priority": "low"
        }

        response = client.put(f"/api/reorder-requests/{pending_reorder.id}",
                            json=update_data,
                            headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["priority"] == "low"

    def test_update_reorder_request_unauthorized_user(self, client, auth_headers_user, pending_reorder):
        """Test updating reorder request by unauthorized user"""
        update_data = {
            "quantity_requested": 200.0
        }

        response = client.put(f"/api/reorder-requests/{pending_reorder.id}",
                            json=update_data,
                            headers=auth_headers_user)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "You do not have permission to update this request" in data["error"]

    def test_update_reorder_request_not_pending(self, client, auth_headers_materials, approved_reorder):
        """Test updating reorder request that is not pending"""
        update_data = {
            "quantity_requested": 100.0
        }

        response = client.put(f"/api/reorder-requests/{approved_reorder.id}",
                            json=update_data,
                            headers=auth_headers_materials)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Can only update pending requests" in data["error"]

    def test_update_reorder_request_not_found(self, client, auth_headers_materials):
        """Test updating non-existent reorder request"""
        update_data = {
            "quantity_requested": 100.0
        }

        response = client.put("/api/reorder-requests/99999",
                            json=update_data,
                            headers=auth_headers_materials)

        assert response.status_code == 404

    def test_update_reorder_request_unauthenticated(self, client, pending_reorder):
        """Test updating reorder request without authentication"""
        update_data = {
            "quantity_requested": 100.0
        }

        response = client.put(f"/api/reorder-requests/{pending_reorder.id}", json=update_data)

        assert response.status_code == 401
