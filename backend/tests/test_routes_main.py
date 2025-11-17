"""
Comprehensive tests for main routes.py endpoints to improve coverage.
Targeting uncovered endpoints including:
- Chemical management (reorder, expiring, archived)
- Tool management (retire, calibration notifications, search)
- User management (CRUD, unlock accounts)
- Registration request handling
- Audit and analytics endpoints
- Profile and password management
"""

import io
import json
from datetime import datetime, timedelta

import pytest

from models import (
    AuditLog,
    Checkout,
    Chemical,
    RegistrationRequest,
    Tool,
    ToolCalibration,
    ToolServiceRecord,
    User,
    UserActivity,
)


class TestChemicalManagementRoutes:
    """Test chemical management endpoints that are uncovered"""

    def test_get_chemicals_reorder_needed(self, client, auth_headers, db_session, test_warehouse):
        """Test getting chemicals that need reordering"""
        # Create a chemical that needs reorder
        chemical = Chemical(
            part_number="REORDER001",
            lot_number="LOT001",
            description="Test Reorder Chemical",
            manufacturer="Test Mfg",
            quantity=10,
            unit="ml",
            location="Storage A",
            warehouse_id=test_warehouse.id,
            needs_reorder=True,
            reorder_status="needed"
        )
        db_session.add(chemical)
        db_session.commit()

        response = client.get("/api/chemicals/reorder-needed", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        # Check that our reorder chemical is in the list
        part_numbers = [c["part_number"] for c in data]
        assert "REORDER001" in part_numbers

    def test_get_chemicals_reorder_needed_unauthorized(self, client, auth_headers_user):
        """Test reorder-needed endpoint without proper permissions"""
        response = client.get("/api/chemicals/reorder-needed", headers=auth_headers_user)

        assert response.status_code == 403

    def test_get_chemicals_on_order(self, client, auth_headers, db_session, test_warehouse):
        """Test getting chemicals that are on order"""
        # Create a chemical that is on order
        chemical = Chemical(
            part_number="ONORDER001",
            lot_number="LOT002",
            description="Test On Order Chemical",
            manufacturer="Test Mfg",
            quantity=5,
            unit="ml",
            location="Storage B",
            warehouse_id=test_warehouse.id,
            reorder_status="ordered"
        )
        db_session.add(chemical)
        db_session.commit()

        response = client.get("/api/chemicals/on-order", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        part_numbers = [c["part_number"] for c in data]
        assert "ONORDER001" in part_numbers

    def test_get_chemicals_expiring_soon(self, client, auth_headers, db_session, test_warehouse):
        """Test getting chemicals expiring soon"""
        # Create a chemical with expiration date within 30 days
        expiring_chemical = Chemical(
            part_number="EXPIRING001",
            lot_number="LOT003",
            description="Expiring Chemical",
            manufacturer="Test Mfg",
            quantity=50,
            unit="ml",
            location="Storage C",
            warehouse_id=test_warehouse.id,
            expiration_date=datetime.utcnow() + timedelta(days=15)
        )
        db_session.add(expiring_chemical)
        db_session.commit()

        response = client.get("/api/chemicals/expiring-soon?days=30", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_archived_chemicals(self, client, auth_headers, db_session, test_warehouse):
        """Test getting archived chemicals"""
        # Create an archived chemical
        archived_chemical = Chemical(
            part_number="ARCHIVED001",
            lot_number="LOT004",
            description="Archived Chemical",
            manufacturer="Test Mfg",
            quantity=0,
            unit="ml",
            location="Archive",
            warehouse_id=test_warehouse.id,
            is_archived=True,
            archived_reason="Expired",
            archived_date=datetime.utcnow()
        )
        db_session.add(archived_chemical)
        db_session.commit()

        response = client.get("/api/chemicals/archived", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_archived_chemicals_with_filters(self, client, auth_headers, db_session, test_warehouse):
        """Test archived chemicals with search filters"""
        archived_chemical = Chemical(
            part_number="FILTERED001",
            lot_number="FILTERLOT",
            description="Filtered Archived Chemical",
            manufacturer="FilterMfg",
            quantity=0,
            unit="ml",
            location="Archive",
            warehouse_id=test_warehouse.id,
            is_archived=True,
            archived_reason="Depleted",
            archived_date=datetime.utcnow(),
            category="Adhesive"
        )
        db_session.add(archived_chemical)
        db_session.commit()

        # Test with category filter
        response = client.get("/api/chemicals/archived?category=Adhesive", headers=auth_headers)
        assert response.status_code == 200

        # Test with search query
        response = client.get("/api/chemicals/archived?q=Filtered", headers=auth_headers)
        assert response.status_code == 200

        # Test with reason filter
        response = client.get("/api/chemicals/archived?reason=Depleted", headers=auth_headers)
        assert response.status_code == 200


class TestHealthAndSystemEndpoints:
    """Test health check and system endpoints"""

    def test_health_check_api_path(self, client):
        """Test health check via /api/health path"""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "timezone" in data

    def test_time_api_endpoint(self, client):
        """Test time API endpoint"""
        response = client.get("/api/time")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ok"
        assert "utc_time" in data
        assert "local_time" in data
        assert "timezone" in data
        assert "using_time_utils" in data

    def test_time_test_endpoint(self, client):
        """Test time test debugging endpoint"""
        response = client.get("/api/time-test")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ok"
        assert "message" in data
        assert "timestamp" in data

    def test_admin_dashboard_test_endpoint(self, client):
        """Test admin dashboard test endpoint"""
        response = client.get("/api/admin/dashboard/test")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert "message" in data
        assert "timestamp" in data

    def test_init_database_already_initialized(self, client, admin_user):
        """Test database initialization when already initialized"""
        response = client.post("/api/admin/init-database")

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False
        assert "already initialized" in data["message"]


class TestRegistrationRequestRoutes:
    """Test admin registration request handling"""

    def test_get_registration_requests_pending(self, client, auth_headers, db_session):
        """Test getting pending registration requests"""
        # Create a pending registration request
        req = RegistrationRequest(
            name="New User",
            employee_number="NEWUSER001",
            department="Engineering",
            status="pending"
        )
        req.set_password("SecurePass123!")
        db_session.add(req)
        db_session.commit()

        response = client.get("/api/admin/registration-requests", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_registration_requests_all(self, client, auth_headers, db_session):
        """Test getting all registration requests"""
        response = client.get("/api/admin/registration-requests?status=all", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_approve_registration_request(self, client, auth_headers, db_session, admin_user):
        """Test approving a registration request"""
        # Create a pending request
        req = RegistrationRequest(
            name="Approve User",
            employee_number="APPROVE001",
            department="Maintenance",
            status="pending"
        )
        req.set_password("SecurePass123!")
        db_session.add(req)
        db_session.commit()

        response = client.post(
            f"/api/admin/registration-requests/{req.id}/approve",
            json={"notes": "Approved by test"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "user_id" in data
        assert data["request_id"] == req.id

        # Verify user was created
        user = User.query.filter_by(employee_number="APPROVE001").first()
        assert user is not None
        assert user.name == "Approve User"

    def test_approve_already_processed_request(self, client, auth_headers, db_session):
        """Test approving an already processed request"""
        req = RegistrationRequest(
            name="Already Approved",
            employee_number="ALREADY001",
            department="IT",
            status="approved"
        )
        req.set_password("Test123!")
        db_session.add(req)
        db_session.commit()

        response = client.post(
            f"/api/admin/registration-requests/{req.id}/approve",
            json={},
            headers=auth_headers
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "already" in data["error"]

    def test_deny_registration_request(self, client, auth_headers, db_session):
        """Test denying a registration request"""
        req = RegistrationRequest(
            name="Deny User",
            employee_number="DENY001",
            department="Finance",
            status="pending"
        )
        req.set_password("SecurePass123!")
        db_session.add(req)
        db_session.commit()

        response = client.post(
            f"/api/admin/registration-requests/{req.id}/deny",
            json={"notes": "Denied for testing"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["request_id"] == req.id

        # Verify request was denied
        db_session.refresh(req)
        assert req.status == "denied"

    def test_deny_already_processed_request(self, client, auth_headers, db_session):
        """Test denying an already processed request"""
        req = RegistrationRequest(
            name="Already Denied",
            employee_number="ALREADYDEN001",
            department="HR",
            status="denied"
        )
        req.set_password("Test123!")
        db_session.add(req)
        db_session.commit()

        response = client.post(
            f"/api/admin/registration-requests/{req.id}/deny",
            json={},
            headers=auth_headers
        )

        assert response.status_code == 400

    def test_registration_requests_unauthorized(self, client, auth_headers_user):
        """Test registration requests without admin privileges"""
        response = client.get("/api/admin/registration-requests", headers=auth_headers_user)

        assert response.status_code == 403


class TestToolManagementRoutes:
    """Test tool management endpoints"""

    def test_retire_tool(self, client, auth_headers, test_tool, db_session):
        """Test retiring a tool"""
        response = client.post(
            f"/api/tools/{test_tool.id}/retire",
            json={"reason": "End of life", "comments": "Tool has exceeded service life"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "Tool retired successfully" in data["message"]
        assert data["tool"]["status"] == "retired"

        # Verify service record was created
        service_record = ToolServiceRecord.query.filter_by(tool_id=test_tool.id).first()
        assert service_record is not None
        assert service_record.action_type == "remove_permanent"

    def test_retire_tool_unauthorized(self, client, auth_headers_user, test_tool):
        """Test retiring tool without admin privileges"""
        response = client.post(
            f"/api/tools/{test_tool.id}/retire",
            json={"reason": "Testing"},
            headers=auth_headers_user
        )

        assert response.status_code == 403

    def test_get_calibration_notifications(self, client, db_session, test_warehouse):
        """Test getting calibration notifications"""
        # Create a tool that requires calibration and is overdue
        overdue_tool = Tool(
            tool_number="CAL001",
            serial_number="CALSERIAL001",
            description="Overdue Calibration Tool",
            condition="Good",
            location="Lab",
            category="Measuring",
            warehouse_id=test_warehouse.id,
            requires_calibration=True,
            calibration_status="overdue",
            next_calibration_date=datetime.now() - timedelta(days=5)
        )
        db_session.add(overdue_tool)

        # Create a tool that is due soon
        due_soon_tool = Tool(
            tool_number="CAL002",
            serial_number="CALSERIAL002",
            description="Due Soon Calibration Tool",
            condition="Good",
            location="Lab",
            category="Measuring",
            warehouse_id=test_warehouse.id,
            requires_calibration=True,
            calibration_status="due_soon",
            next_calibration_date=datetime.now() + timedelta(days=10)
        )
        db_session.add(due_soon_tool)
        db_session.commit()

        response = client.get("/api/calibrations/notifications")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "notifications" in data
        assert "count" in data
        assert "overdue_count" in data
        assert "due_soon_count" in data
        assert data["count"] >= 2

    def test_delete_tool_with_history_blocked(self, client, auth_headers, test_tool, regular_user, db_session):
        """Test that deleting a tool with history is blocked"""
        # Create checkout history for the tool
        checkout = Checkout(
            tool_id=test_tool.id,
            user_id=regular_user.id,
            checkout_date=datetime.utcnow(),
            return_date=datetime.utcnow()
        )
        db_session.add(checkout)
        db_session.commit()

        response = client.delete(
            f"/api/tools/{test_tool.id}",
            headers=auth_headers
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["has_history"] is True
        assert data["has_checkouts"] is True

    def test_delete_tool_force_delete(self, client, auth_headers, db_session, test_warehouse):
        """Test force deleting a tool with history"""
        # Create a tool
        tool = Tool(
            tool_number="FORCEDEL001",
            serial_number="FD001",
            description="Force Delete Tool",
            condition="Good",
            location="Test",
            warehouse_id=test_warehouse.id
        )
        db_session.add(tool)
        db_session.commit()

        response = client.delete(
            f"/api/tools/{tool.id}?force_delete=true",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "deleted successfully" in data["message"]

    def test_delete_tool_unauthorized(self, client, auth_headers_user, test_tool):
        """Test deleting tool without admin privileges"""
        response = client.delete(
            f"/api/tools/{test_tool.id}",
            headers=auth_headers_user
        )

        assert response.status_code == 403

    def test_update_tool_duplicate_check(self, client, auth_headers, test_tool, db_session, test_warehouse):
        """Test updating tool with duplicate tool_number/serial_number"""
        # Create another tool
        other_tool = Tool(
            tool_number="EXISTING001",
            serial_number="EXISTINGSER001",
            description="Existing Tool",
            condition="Good",
            location="Storage",
            warehouse_id=test_warehouse.id
        )
        db_session.add(other_tool)
        db_session.commit()

        # Try to update test_tool with existing combination
        response = client.put(
            f"/api/tools/{test_tool.id}",
            json={"tool_number": "EXISTING001", "serial_number": "EXISTINGSER001"},
            headers=auth_headers
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "already exists" in data["error"]

    def test_create_tool_validation_errors(self, client, auth_headers, test_warehouse):
        """Test creating tool with validation errors"""
        # Missing required field
        response = client.post(
            "/api/tools",
            json={"tool_number": "T123", "warehouse_id": test_warehouse.id},
            headers=auth_headers
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Missing required field" in data["error"]

    def test_create_tool_invalid_warehouse(self, client, auth_headers):
        """Test creating tool with invalid warehouse"""
        response = client.post(
            "/api/tools",
            json={
                "tool_number": "INVALID001",
                "serial_number": "INV001",
                "warehouse_id": 99999
            },
            headers=auth_headers
        )

        assert response.status_code == 400

    def test_tools_pagination_validation(self, client):
        """Test tools endpoint pagination validation"""
        # Invalid page number
        response = client.get("/api/tools?page=0")
        assert response.status_code == 400

        # Invalid per_page
        response = client.get("/api/tools?per_page=0")
        assert response.status_code == 400

        response = client.get("/api/tools?per_page=501")
        assert response.status_code == 400

    def test_search_tools(self, client, test_tool):
        """Test tool search endpoint"""
        response = client.get(f"/api/tools/search?q={test_tool.tool_number}")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["tool_number"] == test_tool.tool_number

    def test_search_tools_no_query(self, client):
        """Test search tools without query parameter"""
        response = client.get("/api/tools/search")

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "query is required" in data["error"]

    def test_get_new_tool_form(self, client, auth_headers):
        """Test getting new tool form data"""
        response = client.get("/api/tools/new", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "form_fields" in data
        assert len(data["form_fields"]) > 0

    def test_get_new_tool_checkouts(self, client, auth_headers_user):
        """Test getting checkouts for new tool (should be empty)"""
        response = client.get("/api/tools/new/checkouts", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []


class TestUserManagementRoutes:
    """Test user management endpoints"""

    def test_get_users_list(self, client, auth_headers, admin_user):
        """Test getting list of users"""
        response = client.get("/api/users", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_users_with_search(self, client, auth_headers, admin_user):
        """Test searching users by employee number"""
        response = client.get(f"/api/users?q={admin_user.employee_number}", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["employee_number"] == admin_user.employee_number

    def test_create_user(self, client, auth_headers):
        """Test creating a new user"""
        user_data = {
            "name": "New Created User",
            "employee_number": "NEWCREATE001",
            "department": "Quality",
            "password": "SecurePass123!@"
        }

        response = client.post("/api/users", json=user_data, headers=auth_headers)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["name"] == "New Created User"
        assert data["employee_number"] == "NEWCREATE001"

    def test_create_user_duplicate_employee_number(self, client, auth_headers, admin_user):
        """Test creating user with duplicate employee number"""
        user_data = {
            "name": "Duplicate User",
            "employee_number": admin_user.employee_number,
            "department": "IT",
            "password": "SecurePass123!@"
        }

        response = client.post("/api/users", json=user_data, headers=auth_headers)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "already exists" in data["error"]

    def test_create_user_weak_password(self, client, auth_headers):
        """Test creating user with weak password"""
        user_data = {
            "name": "Weak Password User",
            "employee_number": "WEAK001",
            "department": "Testing",
            "password": "weak"
        }

        response = client.post("/api/users", json=user_data, headers=auth_headers)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "security requirements" in data["error"]

    def test_create_user_missing_fields(self, client, auth_headers):
        """Test creating user with missing required fields"""
        user_data = {
            "name": "Incomplete User"
        }

        response = client.post("/api/users", json=user_data, headers=auth_headers)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Missing required field" in data["error"]

    def test_get_user_detail(self, client, auth_headers, admin_user):
        """Test getting user detail by ID"""
        response = client.get(f"/api/users/{admin_user.id}", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["id"] == admin_user.id
        assert data["name"] == admin_user.name

    def test_update_user(self, client, auth_headers, regular_user):
        """Test updating user information"""
        update_data = {
            "name": "Updated User Name",
            "department": "Updated Department"
        }

        response = client.put(
            f"/api/users/{regular_user.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Updated User Name"
        assert data["department"] == "Updated Department"

    def test_update_user_password(self, client, auth_headers, db_session):
        """Test updating user password as admin"""
        # Create a test user
        user = User(
            name="Password Update Test",
            employee_number="PWDUPD001",
            department="Test",
            is_admin=False,
            is_active=True
        )
        user.set_password("OldPass123!")
        db_session.add(user)
        db_session.commit()

        response = client.put(
            f"/api/users/{user.id}",
            json={"password": "NewSecurePass123!@"},
            headers=auth_headers
        )

        assert response.status_code == 200

    def test_update_user_weak_password_rejected(self, client, auth_headers, regular_user):
        """Test updating user with weak password is rejected"""
        response = client.put(
            f"/api/users/{regular_user.id}",
            json={"password": "weak"},
            headers=auth_headers
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "security requirements" in data["error"]

    def test_deactivate_user(self, client, auth_headers, db_session):
        """Test deactivating (soft deleting) a user"""
        user = User(
            name="To Be Deactivated",
            employee_number="DEACT001",
            department="Test",
            is_admin=False,
            is_active=True
        )
        user.set_password("Test123!")
        db_session.add(user)
        db_session.commit()

        response = client.delete(f"/api/users/{user.id}", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "deactivated successfully" in data["message"]

        # Verify user is deactivated
        db_session.refresh(user)
        assert user.is_active is False

    def test_unlock_user_account(self, client, auth_headers, db_session):
        """Test unlocking a locked user account"""
        user = User(
            name="Locked User",
            employee_number="LOCKED001",
            department="Test",
            is_admin=False,
            is_active=True
        )
        user.set_password("Test123!")
        # Set lockout fields after creation using correct field names
        user.failed_login_attempts = 10
        user.account_locked_until = datetime.utcnow() + timedelta(hours=1)
        db_session.add(user)
        db_session.commit()

        response = client.post(f"/api/users/{user.id}/unlock", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "successfully unlocked" in data["message"]
        assert data["user"]["id"] == user.id

    def test_unlock_user_not_locked(self, client, auth_headers, regular_user):
        """Test unlocking a user that isn't locked"""
        response = client.post(f"/api/users/{regular_user.id}/unlock", headers=auth_headers)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "not locked" in data["message"]

    def test_users_unauthorized_access(self, client, auth_headers_user):
        """Test user management without proper permissions"""
        response = client.get("/api/users", headers=auth_headers_user)

        assert response.status_code == 403


class TestCheckoutRoutes:
    """Test checkout-related endpoints"""

    def test_get_all_checkouts(self, client, db_session, test_tool, regular_user):
        """Test getting all checkouts"""
        # Create a checkout
        checkout = Checkout(
            tool_id=test_tool.id,
            user_id=regular_user.id
        )
        db_session.add(checkout)
        db_session.commit()

        response = client.get("/api/checkouts")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_create_checkout_invalid_tool_id(self, client, auth_headers_user):
        """Test creating checkout with invalid tool ID"""
        response = client.post(
            "/api/checkouts",
            json={"tool_id": "invalid"},
            headers=auth_headers_user
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Invalid tool ID" in data["error"]

    def test_create_checkout_nonexistent_tool(self, client, auth_headers_user):
        """Test creating checkout for nonexistent tool"""
        response = client.post(
            "/api/checkouts",
            json={"tool_id": 99999},
            headers=auth_headers_user
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert "does not exist" in data["error"]

    def test_create_checkout_already_checked_out(self, client, auth_headers_user, test_tool, regular_user, db_session):
        """Test checking out an already checked out tool"""
        # Create active checkout
        checkout = Checkout(
            tool_id=test_tool.id,
            user_id=regular_user.id
        )
        db_session.add(checkout)
        db_session.commit()

        response = client.post(
            "/api/checkouts",
            json={"tool_id": test_tool.id},
            headers=auth_headers_user
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "already checked out" in data["error"]

    def test_create_checkout_with_user_id(self, client, auth_headers, test_tool, regular_user):
        """Test creating checkout for specific user"""
        response = client.post(
            "/api/checkouts",
            json={
                "tool_id": test_tool.id,
                "user_id": regular_user.id,
                "expected_return_date": "2025-12-31"
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert "id" in data

    def test_get_user_checkouts(self, client, auth_headers_user, test_tool, regular_user, db_session):
        """Test getting current user's checkouts"""
        # Create a checkout for the user
        checkout = Checkout(
            tool_id=test_tool.id,
            user_id=regular_user.id
        )
        db_session.add(checkout)
        db_session.commit()

        response = client.get("/api/checkouts/user", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_overdue_checkouts(self, client, auth_headers, test_tool, regular_user, db_session):
        """Test getting overdue checkouts"""
        # Create an overdue checkout
        checkout = Checkout(
            tool_id=test_tool.id,
            user_id=regular_user.id,
            expected_return_date=datetime.now() - timedelta(days=5)
        )
        db_session.add(checkout)
        db_session.commit()

        response = client.get("/api/checkouts/overdue", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["days_overdue"] >= 5

    def test_return_checkout_not_found(self, client, auth_headers):
        """Test returning non-existent checkout"""
        response = client.post("/api/checkouts/99999/return", headers=auth_headers)

        assert response.status_code == 404

    def test_return_already_returned(self, client, auth_headers, test_tool, regular_user, db_session):
        """Test returning an already returned tool"""
        checkout = Checkout(
            tool_id=test_tool.id,
            user_id=regular_user.id,
            return_date=datetime.utcnow()
        )
        db_session.add(checkout)
        db_session.commit()

        response = client.post(
            f"/api/checkouts/{checkout.id}/return",
            headers=auth_headers
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "already been returned" in data["error"]


class TestAuditRoutes:
    """Test audit log endpoints"""

    def test_get_audit_logs(self, client, auth_headers, db_session):
        """Test getting audit logs"""
        # Create some audit logs
        log = AuditLog(
            action_type="test_action",
            action_details="Test audit log entry"
        )
        db_session.add(log)
        db_session.commit()

        response = client.get("/api/audit", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_audit_logs_unauthorized(self, client, auth_headers_user):
        """Test audit logs without admin privileges"""
        response = client.get("/api/audit", headers=auth_headers_user)

        assert response.status_code == 403

    def test_get_paginated_audit_logs(self, client):
        """Test getting paginated audit logs"""
        response = client.get("/api/audit/logs?page=1&limit=10")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_audit_metrics(self, client):
        """Test getting audit metrics"""
        response = client.get("/api/audit/metrics?timeframe=week")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["timeframe"] == "week"
        assert "total_activity" in data
        assert "checkouts" in data
        assert "returns" in data
        assert "daily_activity" in data

    def test_get_audit_metrics_different_timeframes(self, client):
        """Test audit metrics with different timeframes"""
        for timeframe in ["day", "week", "month"]:
            response = client.get(f"/api/audit/metrics?timeframe={timeframe}")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["timeframe"] == timeframe

    def test_get_user_audit_logs(self, client, regular_user, db_session):
        """Test getting audit logs for specific user"""
        # Create user activity
        activity = UserActivity(
            user_id=regular_user.id,
            activity_type="test",
            description="Test activity"
        )
        db_session.add(activity)
        db_session.commit()

        response = client.get(f"/api/audit/users/{regular_user.id}?page=1&limit=10")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_tool_audit_logs(self, client, test_tool, db_session):
        """Test getting audit logs for specific tool"""
        # Create tool-related audit log
        log = AuditLog(
            action_type="tool_action",
            action_details=f"Action on tool {test_tool.id}"
        )
        db_session.add(log)
        db_session.commit()

        response = client.get(f"/api/audit/tools/{test_tool.id}?page=1&limit=10")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)


class TestAuthenticationRoutes:
    """Test authentication-related endpoints"""

    def test_register_user_success(self, client, db_session):
        """Test successful user registration"""
        reg_data = {
            "name": "New Registration",
            "employee_number": "NEWREG001",
            "department": "Operations",
            "password": "SecurePass123!@",
            "confirm_password": "SecurePass123!@"
        }

        response = client.post("/api/auth/register", json=reg_data)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert "submitted" in data["message"]

    def test_register_user_password_mismatch(self, client):
        """Test registration with password mismatch"""
        reg_data = {
            "name": "Mismatch User",
            "employee_number": "MISMATCH001",
            "department": "Test",
            "password": "Password123!",
            "confirm_password": "DifferentPass123!"
        }

        response = client.post("/api/auth/register", json=reg_data)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "do not match" in data["error"]

    def test_register_user_existing_employee_number(self, client, admin_user):
        """Test registration with existing employee number"""
        reg_data = {
            "name": "Duplicate Employee",
            "employee_number": admin_user.employee_number,
            "department": "Test",
            "password": "SecurePass123!@"
        }

        response = client.post("/api/auth/register", json=reg_data)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "already registered" in data["error"]

    def test_register_user_pending_request_exists(self, client, db_session):
        """Test registration when pending request already exists"""
        # Create pending registration request
        req = RegistrationRequest(
            name="Pending User",
            employee_number="PENDING001",
            department="Test",
            status="pending"
        )
        req.set_password("Test123!")
        db_session.add(req)
        db_session.commit()

        reg_data = {
            "name": "Another User",
            "employee_number": "PENDING001",
            "department": "Test",
            "password": "SecurePass123!@"
        }

        response = client.post("/api/auth/register", json=reg_data)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "already pending" in data["error"]

    def test_register_user_weak_password(self, client):
        """Test registration with weak password"""
        reg_data = {
            "name": "Weak Password",
            "employee_number": "WEAKPWD001",
            "department": "Test",
            "password": "weak"
        }

        response = client.post("/api/auth/register", json=reg_data)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "security requirements" in data["error"]

    def test_register_user_missing_fields(self, client):
        """Test registration with missing fields"""
        reg_data = {
            "name": "Incomplete"
        }

        response = client.post("/api/auth/register", json=reg_data)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Missing required field" in data["error"]

    def test_get_user_profile(self, client, auth_headers_user, regular_user):
        """Test getting authenticated user profile"""
        response = client.get("/api/auth/user", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["id"] == regular_user.id

    def test_get_user_activity(self, client, auth_headers_user, regular_user, db_session):
        """Test getting user's own activity"""
        # Create some activities
        for i in range(3):
            activity = UserActivity(
                user_id=regular_user.id,
                activity_type="test",
                description=f"Activity {i}"
            )
            db_session.add(activity)
        db_session.commit()

        response = client.get("/api/user/activity", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 3


class TestProfileAndPasswordRoutes:
    """Test user profile and password management"""

    def test_update_profile_avatar(self, client, auth_headers_user, regular_user):
        """Test updating user profile with avatar URL"""
        response = client.put(
            "/api/user/profile",
            json={"avatar": "/api/static/avatars/test.png"},
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["avatar"] == "/api/static/avatars/test.png"

    def test_upload_avatar_no_file(self, client, auth_headers_user):
        """Test avatar upload without file"""
        response = client.post("/api/user/avatar", headers=auth_headers_user)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "No file part" in data["error"]

    def test_upload_avatar_empty_filename(self, client, auth_headers_user):
        """Test avatar upload with empty filename"""
        data = {"avatar": (io.BytesIO(b""), "")}
        response = client.post(
            "/api/user/avatar",
            data=data,
            headers=auth_headers_user,
            content_type="multipart/form-data"
        )

        assert response.status_code == 400

    def test_change_password_missing_fields(self, client, auth_headers_user, regular_user, db_session):
        """Test password change with missing fields"""
        # Ensure JWT isn't stale by adjusting password_changed_at
        if regular_user.password_changed_at:
            regular_user.password_changed_at -= timedelta(seconds=10)
            db_session.commit()

        response = client.put(
            "/api/user/password",
            json={"current_password": "user123"},
            headers=auth_headers_user
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Missing required field" in data["error"]

    def test_change_password_weak_new_password(self, client, auth_headers_user, regular_user, db_session):
        """Test password change with weak new password"""
        if regular_user.password_changed_at:
            regular_user.password_changed_at -= timedelta(seconds=5)
            db_session.commit()

        response = client.put(
            "/api/user/password",
            json={"current_password": "user123", "new_password": "weak"},
            headers=auth_headers_user
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "security requirements" in data["error"]


class TestAnalyticsRoutes:
    """Test analytics endpoints"""

    def test_get_usage_analytics(self, client, auth_headers):
        """Test getting usage analytics"""
        response = client.get("/api/analytics/usage?timeframe=week", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["timeframe"] == "week"
        assert "checkoutsByDepartment" in data
        assert "checkoutsByDay" in data
        assert "toolUsageByCategory" in data
        assert "mostFrequentlyCheckedOut" in data

    def test_get_usage_analytics_different_timeframes(self, client, auth_headers):
        """Test usage analytics with different timeframes"""
        for timeframe in ["day", "week", "month", "quarter", "year"]:
            response = client.get(f"/api/analytics/usage?timeframe={timeframe}", headers=auth_headers)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["timeframe"] == timeframe

    def test_get_usage_analytics_unauthorized(self, client, auth_headers_user):
        """Test usage analytics without proper permissions"""
        response = client.get("/api/analytics/usage", headers=auth_headers_user)

        assert response.status_code == 403


class TestStaticFileServing:
    """Test static file serving endpoints"""

    def test_serve_static_not_found(self, client):
        """Test serving non-existent static file"""
        response = client.get("/api/static/nonexistent.txt")

        # Should return 404 for non-existent file
        assert response.status_code == 404


class TestToolCalibrationUpdates:
    """Test tool calibration field updates"""

    def test_update_tool_calibration_frequency(self, client, auth_headers, db_session, test_warehouse):
        """Test updating tool calibration frequency recalculates next date"""
        tool = Tool(
            tool_number="CALFREQ001",
            serial_number="CALFREQS001",
            description="Calibration Frequency Test Tool",
            condition="Good",
            location="Lab",
            warehouse_id=test_warehouse.id,
            requires_calibration=True,
            calibration_frequency_days=30,
            last_calibration_date=datetime.now() - timedelta(days=10),
            calibration_status="current"
        )
        db_session.add(tool)
        db_session.commit()

        response = client.put(
            f"/api/tools/{tool.id}",
            json={"calibration_frequency_days": 60},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["calibration_frequency_days"] == 60

    def test_disable_tool_calibration(self, client, auth_headers, db_session, test_warehouse):
        """Test disabling calibration requirement"""
        tool = Tool(
            tool_number="CALDIS001",
            serial_number="CALDISS001",
            description="Disable Calibration Tool",
            condition="Good",
            location="Lab",
            warehouse_id=test_warehouse.id,
            requires_calibration=True,
            calibration_status="current"
        )
        db_session.add(tool)
        db_session.commit()

        response = client.put(
            f"/api/tools/{tool.id}",
            json={"requires_calibration": False},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["requires_calibration"] is False
        assert data["calibration_status"] == "not_applicable"

    def test_enable_tool_calibration(self, client, auth_headers, db_session, test_warehouse):
        """Test enabling calibration requirement"""
        tool = Tool(
            tool_number="CALEN001",
            serial_number="CALENS001",
            description="Enable Calibration Tool",
            condition="Good",
            location="Lab",
            warehouse_id=test_warehouse.id,
            requires_calibration=False
        )
        db_session.add(tool)
        db_session.commit()

        response = client.put(
            f"/api/tools/{tool.id}",
            json={"requires_calibration": True},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["requires_calibration"] is True
