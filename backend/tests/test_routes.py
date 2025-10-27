"""
Tests for API routes and endpoints
"""

import json
from datetime import timedelta

from models import Checkout, Chemical, Tool


class TestHealthEndpoints:
    """Test health and status endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestToolRoutes:
    """Test tool management routes"""

    def test_get_tools_authenticated(self, client, auth_headers_user, test_tool):
        """Test getting tools list with authentication"""
        response = client.get("/api/tools", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        # API now returns paginated response
        assert "tools" in data
        assert "pagination" in data
        assert isinstance(data["tools"], list)
        assert len(data["tools"]) >= 1

        # Results are paginated and may include tools created by other tests,
        # so verify that our known tool is present anywhere in the payload.
        tool_numbers = {tool["tool_number"] for tool in data["tools"]}
        assert "T001" in tool_numbers

    def test_get_tools_unauthenticated(self, client, test_tool):
        """Test getting tools list without authentication"""
        response = client.get("/api/tools")

        # API no longer requires authentication for GET
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "tools" in data

    def test_get_tool_by_id(self, client, auth_headers_user, test_tool):
        """Test getting specific tool by ID"""
        response = client.get(f"/api/tools/{test_tool.id}", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["id"] == test_tool.id
        assert data["tool_number"] == "T001"
        assert data["description"] == "Test Tool"

    def test_create_tool_admin(self, client, auth_headers_admin, db_session, test_warehouse):
        """Test creating tool as admin"""
        tool_data = {
            "tool_number": "T002",
            "serial_number": "S002",
            "description": "New Test Tool",
            "condition": "Excellent",
            "location": "Lab A",
            "category": "Testing",
            "warehouse_id": test_warehouse.id
        }

        response = client.post("/api/tools",
                             json=tool_data,
                             headers=auth_headers_admin)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data["tool_number"] == "T002"
        assert data["description"] == "New Test Tool"

        # Verify tool was created in database
        tool = Tool.query.filter_by(tool_number="T002").first()
        assert tool is not None

    def test_create_tool_regular_user(self, client, auth_headers_user):
        """Test creating tool as regular user (should fail)"""
        tool_data = {
            "tool_number": "T003",
            "serial_number": "S003",
            "description": "Unauthorized Tool"
        }

        response = client.post("/api/tools",
                             json=tool_data,
                             headers=auth_headers_user)

        assert response.status_code == 403
        data = json.loads(response.data)
        assert "required" in data["error"].lower()

    def test_update_tool_admin(self, client, auth_headers_admin, test_tool):
        """Test updating tool as admin"""
        update_data = {
            "description": "Updated Test Tool",
            "condition": "Fair"
        }

        response = client.put(f"/api/tools/{test_tool.id}",
                            json=update_data,
                            headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["description"] == "Updated Test Tool"
        assert data["condition"] == "Fair"

    def test_checkout_tool(self, client, auth_headers_user, test_tool, db_session):
        """Test checking out a tool"""
        checkout_data = {
            "tool_id": test_tool.id,
            "expected_return_date": "2024-12-31T23:59:59"
        }

        response = client.post("/api/checkouts",
                               json=checkout_data,
                               headers=auth_headers_user)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert "id" in data
        assert data["message"].startswith("Tool")

        # Verify checkout was created
        checkout = Checkout.query.get(data["id"])
        assert checkout is not None
        assert checkout.tool_id == test_tool.id
        assert checkout.return_date is None

    def test_return_tool(self, client, auth_headers_materials, test_tool, regular_user, db_session):
        """Test returning a tool"""
        # First create a checkout
        checkout = Checkout(
            tool_id=test_tool.id,
            user_id=regular_user.id
        )
        db_session.add(checkout)
        db_session.commit()

        response = client.post(f"/api/checkouts/{checkout.id}/return",
                               headers=auth_headers_materials,
                               json={})

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["status"] == "Returned"
        assert data["tool_id"] == test_tool.id

        # Verify checkout was updated
        db_session.refresh(checkout)
        assert checkout.return_date is not None


class TestChemicalRoutes:
    """Test chemical management routes"""

    def test_get_chemicals_materials_user(self, client, auth_headers_materials, test_chemical):
        """Test getting chemicals as materials user"""
        response = client.get("/api/chemicals", headers=auth_headers_materials)

        assert response.status_code == 200
        data = json.loads(response.data)

        # API now returns paginated response
        assert "chemicals" in data
        assert "pagination" in data
        assert isinstance(data["chemicals"], list)
        assert len(data["chemicals"]) >= 1

        # Multiple chemicals can exist, so ensure our fixture is represented
        # instead of relying on list ordering.
        part_numbers = {chem["part_number"] for chem in data["chemicals"]}
        assert "C001" in part_numbers

    def test_get_chemicals_regular_user(self, client, auth_headers_user, test_chemical):
        """Test getting chemicals as regular user"""
        response = client.get("/api/chemicals", headers=auth_headers_user)

        # API no longer requires special permissions for GET
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "chemicals" in data
        assert isinstance(data["chemicals"], list)

    def test_create_chemical_materials_user(self, client, auth_headers_materials, db_session, test_warehouse):
        """Test creating chemical as materials user"""
        chemical_data = {
            "part_number": "C002",
            "lot_number": "L002",
            "description": "New Test Chemical",
            "manufacturer": "Test Manufacturer",
            "quantity": 50.0,
            "unit": "ml",
            "location": "Storage A",
            "warehouse_id": test_warehouse.id
        }

        response = client.post("/api/chemicals",
                             json=chemical_data,
                             headers=auth_headers_materials)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data["part_number"] == "C002"
        assert data["description"] == "New Test Chemical"

        # Verify chemical was created
        chemical = Chemical.query.filter_by(part_number="C002").first()
        assert chemical is not None


class TestUserRoutes:
    """Test user management routes"""

    def test_get_profile(self, client, auth_headers_user, regular_user):
        """Test getting user profile"""
        response = client.get("/api/auth/user", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["employee_number"] == "USER001"
        assert data["name"] == "Test User"
        assert data["is_admin"] is False

    def test_update_profile(self, client, auth_headers_user, regular_user):
        """Test updating user profile"""
        update_data = {
            "name": "Updated Test User",
            "department": "Updated Engineering"
        }

        response = client.put("/api/user/profile",
                            json=update_data,
                            headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["name"] == "Updated Test User"
        assert data["department"] == "Updated Engineering"

    def test_change_password(self, client, auth_headers_user, regular_user, db_session):
        """Test changing user password"""
        if regular_user.password_changed_at:
            regular_user.password_changed_at -= timedelta(seconds=5)
            db_session.commit()

        password_data = {
            "current_password": "user123",
            "new_password": "NewPassword123!"
        }

        response = client.put("/api/user/password",
                            json=password_data,
                            headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["message"] == "Password changed successfully"

    def test_change_password_wrong_current(self, client, auth_headers_user, regular_user, db_session):
        """Test changing password with wrong current password"""
        if regular_user.password_changed_at:
            regular_user.password_changed_at -= timedelta(seconds=5)
            db_session.commit()

        password_data = {
            "current_password": "wrongpassword",
            "new_password": "NewPassword123!"
        }

        response = client.put("/api/user/password",
                            json=password_data,
                            headers=auth_headers_user)

        assert response.status_code == 400
        data = json.loads(response.data)

        assert "incorrect" in data["error"].lower()


class TestAdminRoutes:
    """Test admin-only routes"""

    def test_admin_dashboard_stats(self, client, auth_headers_admin, test_tool, test_chemical):
        """Test admin dashboard stats endpoint"""
        response = client.get("/api/admin/dashboard/stats", headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "counts" in data
        assert "tools" in data["counts"]
        assert "users" in data["counts"]
        assert data["counts"]["tools"] >= 1

    def test_admin_dashboard_stats_regular_user(self, client, auth_headers_user):
        """Test admin dashboard stats as regular user (should fail)"""
        response = client.get("/api/admin/dashboard/stats", headers=auth_headers_user)

        assert response.status_code == 403
        data = json.loads(response.data)

        assert "admin" in data["error"].lower() or "required" in data["error"].lower()
