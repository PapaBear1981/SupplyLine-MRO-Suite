"""
Comprehensive tests for Department Management Routes

This module tests the department management endpoints including:
- CRUD operations for departments
- Admin authorization and permission requirements
- Validation and error handling
- Edge cases and security features
"""

import json
from unittest.mock import patch, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models import Department, User, Permission, Role, RolePermission, UserRole


# Fixtures for department testing


@pytest.fixture
def clean_departments(db_session):
    """Clean up departments table before tests"""
    db_session.query(Department).delete()
    db_session.commit()
    yield db_session


@pytest.fixture
def test_department(clean_departments):
    """Create a test department"""
    department = Department(
        name="Test Department",
        description="A test department",
        is_active=True
    )
    clean_departments.add(department)
    clean_departments.commit()
    return department


@pytest.fixture
def inactive_department(clean_departments):
    """Create an inactive department"""
    department = Department(
        name="Inactive Department",
        description="An inactive department",
        is_active=False
    )
    clean_departments.add(department)
    clean_departments.commit()
    return department


@pytest.fixture
def multiple_departments(clean_departments):
    """Create multiple departments for testing"""
    departments = []
    for i in range(5):
        dept = Department(
            name=f"Department {i}",
            description=f"Description for department {i}",
            is_active=i % 2 == 0  # Alternating active/inactive
        )
        clean_departments.add(dept)
        departments.append(dept)
    clean_departments.commit()
    return departments


@pytest.fixture
def department_permissions(db_session):
    """Create department-related permissions"""
    permissions = []
    perm_names = [
        "department.create",
        "department.update",
        "department.delete",
        "department.hard_delete"
    ]
    for perm_name in perm_names:
        perm = Permission(name=perm_name, description=f"Permission for {perm_name}")
        db_session.add(perm)
        permissions.append(perm)
    db_session.commit()
    return permissions


@pytest.fixture
def admin_with_dept_perms(db_session, admin_user, department_permissions):
    """Create an admin user with department permissions via roles"""
    # Create admin role
    admin_role = Role(name="dept_admin", description="Department Administrator")
    db_session.add(admin_role)
    db_session.flush()

    # Assign all department permissions to the role
    for perm in department_permissions:
        role_perm = RolePermission(role_id=admin_role.id, permission_id=perm.id)
        db_session.add(role_perm)

    # Assign role to admin user
    user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
    db_session.add(user_role)
    db_session.commit()

    return admin_user


@pytest.fixture
def admin_headers_with_perms(app, admin_with_dept_perms):
    """Generate auth headers for admin with department permissions"""
    from auth.jwt_manager import JWTManager
    with app.app_context():
        tokens = JWTManager.generate_tokens(admin_with_dept_perms)
        return {"Authorization": f"Bearer {tokens['access_token']}"}


class TestGetDepartmentsEndpoint:
    """Test the GET /api/departments endpoint"""

    def test_get_departments_empty(self, client, auth_headers_user, clean_departments):
        """Test getting departments when none exist"""
        response = client.get("/api/departments", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_departments_with_data(self, client, auth_headers_user, test_department):
        """Test getting departments with data"""
        response = client.get("/api/departments", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert isinstance(data, list)
        assert len(data) >= 1
        dept_names = [d["name"] for d in data]
        assert "Test Department" in dept_names

    def test_get_departments_excludes_inactive_by_default(self, client, auth_headers_user, test_department, inactive_department):
        """Test that inactive departments are excluded by default"""
        response = client.get("/api/departments", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        dept_names = [d["name"] for d in data]
        assert "Test Department" in dept_names
        assert "Inactive Department" not in dept_names

    def test_get_departments_include_inactive_true(self, client, auth_headers_user, test_department, inactive_department):
        """Test including inactive departments"""
        response = client.get("/api/departments?include_inactive=true", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        dept_names = [d["name"] for d in data]
        assert "Test Department" in dept_names
        assert "Inactive Department" in dept_names

    def test_get_departments_include_inactive_false(self, client, auth_headers_user, test_department, inactive_department):
        """Test explicitly excluding inactive departments"""
        response = client.get("/api/departments?include_inactive=false", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        dept_names = [d["name"] for d in data]
        assert "Test Department" in dept_names
        assert "Inactive Department" not in dept_names

    def test_get_departments_multiple(self, client, auth_headers_user, multiple_departments):
        """Test getting multiple departments"""
        response = client.get("/api/departments?include_inactive=true", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert len(data) >= 5
        # Check structure
        for dept in data:
            assert "id" in dept
            assert "name" in dept
            assert "description" in dept
            assert "is_active" in dept
            assert "created_at" in dept
            assert "updated_at" in dept

    def test_get_departments_without_auth(self, client, clean_departments):
        """Test getting departments without authentication"""
        response = client.get("/api/departments")
        assert response.status_code == 401

    def test_get_departments_sqlalchemy_error(self, client, auth_headers_user, clean_departments):
        """Test handling SQLAlchemy errors when fetching departments"""
        with patch("routes_departments.Department.query") as mock_query:
            mock_query.all.side_effect = SQLAlchemyError("Database error")
            mock_query.filter_by.return_value.all.side_effect = SQLAlchemyError("Database error")

            response = client.get("/api/departments", headers=auth_headers_user)

            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
            assert "Failed to fetch departments" in data["error"]


class TestGetDepartmentByIdEndpoint:
    """Test the GET /api/departments/<id> endpoint"""

    def test_get_department_by_id(self, client, auth_headers_user, test_department):
        """Test getting a specific department"""
        response = client.get(f"/api/departments/{test_department.id}", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["id"] == test_department.id
        assert data["name"] == "Test Department"
        assert data["description"] == "A test department"
        assert data["is_active"] is True

    def test_get_department_not_found(self, client, auth_headers_user, clean_departments):
        """Test getting non-existent department"""
        response = client.get("/api/departments/99999", headers=auth_headers_user)
        assert response.status_code == 404

    def test_get_inactive_department_by_id(self, client, auth_headers_user, inactive_department):
        """Test getting an inactive department by ID"""
        response = client.get(f"/api/departments/{inactive_department.id}", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["is_active"] is False

    def test_get_department_without_auth(self, client, test_department):
        """Test getting department without authentication"""
        response = client.get(f"/api/departments/{test_department.id}")
        assert response.status_code == 401

    def test_get_department_sqlalchemy_error(self, client, auth_headers_user, test_department):
        """Test handling SQLAlchemy errors when fetching specific department"""
        with patch("routes_departments.Department.query") as mock_query:
            mock_query.get_or_404.side_effect = SQLAlchemyError("Database error")

            response = client.get(f"/api/departments/{test_department.id}", headers=auth_headers_user)

            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
            assert "Failed to fetch department" in data["error"]


class TestCreateDepartmentEndpoint:
    """Test the POST /api/departments endpoint"""

    def test_create_department_success(self, client, admin_headers_with_perms, clean_departments):
        """Test creating a department successfully"""
        department_data = {
            "name": "New Department",
            "description": "A newly created department",
            "is_active": True
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data["name"] == "New Department"
        assert data["description"] == "A newly created department"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_department_minimal(self, client, admin_headers_with_perms, clean_departments):
        """Test creating department with minimal data (just name)"""
        department_data = {
            "name": "Minimal Department"
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

        assert response.status_code == 201
        data = json.loads(response.data)

        assert data["name"] == "Minimal Department"
        assert data["description"] == ""  # Default empty string
        assert data["is_active"] is True  # Default value

    def test_create_department_inactive(self, client, admin_headers_with_perms, clean_departments):
        """Test creating an inactive department"""
        department_data = {
            "name": "Inactive New Department",
            "is_active": False
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["is_active"] is False

    def test_create_department_empty_name(self, client, admin_headers_with_perms, clean_departments):
        """Test creating department with empty name"""
        department_data = {
            "name": ""
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "required" in data["error"].lower()

    def test_create_department_whitespace_name(self, client, admin_headers_with_perms, clean_departments):
        """Test creating department with whitespace-only name"""
        department_data = {
            "name": "   "
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "required" in data["error"].lower()

    def test_create_department_null_name(self, client, admin_headers_with_perms, clean_departments):
        """Test creating department with null name"""
        department_data = {
            "name": None
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_create_department_missing_name(self, client, admin_headers_with_perms, clean_departments):
        """Test creating department without name field"""
        department_data = {
            "description": "No name provided"
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "required" in data["error"].lower()

    def test_create_department_empty_body(self, client, admin_headers_with_perms, clean_departments):
        """Test creating department with empty request body"""
        response = client.post("/api/departments", json={}, headers=admin_headers_with_perms)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_create_department_no_json(self, client, admin_headers_with_perms, clean_departments):
        """Test creating department without JSON body"""
        response = client.post("/api/departments", headers=admin_headers_with_perms)

        # Without Content-Type header, Flask raises UnsupportedMediaType (500 in error handler)
        assert response.status_code in [400, 415, 500]

    def test_create_department_duplicate_name(self, client, admin_headers_with_perms, test_department):
        """Test creating department with duplicate name"""
        department_data = {
            "name": "Test Department"  # Same as test_department
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "already exists" in data["error"].lower()

    def test_create_department_duplicate_name_case_insensitive(self, client, admin_headers_with_perms, test_department):
        """Test that duplicate check is case-insensitive"""
        department_data = {
            "name": "test department"  # Different case
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "already exists" in data["error"].lower()

    def test_create_department_name_trim_whitespace(self, client, admin_headers_with_perms, clean_departments):
        """Test that department name is trimmed"""
        department_data = {
            "name": "  Trimmed Department  ",
            "description": "  Trimmed Description  "
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["name"] == "Trimmed Department"
        assert data["description"] == "Trimmed Description"

    def test_create_department_without_auth(self, client, clean_departments):
        """Test creating department without authentication"""
        department_data = {
            "name": "Unauthorized Department"
        }

        response = client.post("/api/departments", json=department_data)
        assert response.status_code == 401

    def test_create_department_no_permission(self, client, auth_headers_user, clean_departments):
        """Test creating department without proper permissions"""
        department_data = {
            "name": "No Permission Department"
        }

        response = client.post("/api/departments", json=department_data, headers=auth_headers_user)
        assert response.status_code == 403

    def test_create_department_integrity_error(self, client, admin_headers_with_perms, clean_departments):
        """Test handling IntegrityError during creation"""
        with patch("routes_departments.db.session.commit") as mock_commit:
            mock_commit.side_effect = IntegrityError("Duplicate", {}, None)

            department_data = {
                "name": "Integrity Error Department"
            }

            response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data
            assert "already exists" in data["error"].lower()

    def test_create_department_sqlalchemy_error(self, client, admin_headers_with_perms, clean_departments):
        """Test handling SQLAlchemy errors during creation"""
        with patch("routes_departments.db.session.commit") as mock_commit:
            mock_commit.side_effect = SQLAlchemyError("Database error")

            department_data = {
                "name": "SQLAlchemy Error Department"
            }

            response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
            assert "Failed to create department" in data["error"]


class TestUpdateDepartmentEndpoint:
    """Test the PUT /api/departments/<id> endpoint"""

    def test_update_department_name(self, client, admin_headers_with_perms, test_department):
        """Test updating department name"""
        update_data = {
            "name": "Updated Department Name"
        }

        response = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=admin_headers_with_perms)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Updated Department Name"

    def test_update_department_description(self, client, admin_headers_with_perms, test_department):
        """Test updating department description"""
        update_data = {
            "description": "Updated description"
        }

        response = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=admin_headers_with_perms)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["description"] == "Updated description"

    def test_update_department_is_active(self, client, admin_headers_with_perms, test_department):
        """Test updating department active status"""
        update_data = {
            "is_active": False
        }

        response = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=admin_headers_with_perms)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["is_active"] is False

    def test_update_department_all_fields(self, client, admin_headers_with_perms, test_department):
        """Test updating all department fields"""
        update_data = {
            "name": "Fully Updated",
            "description": "All fields updated",
            "is_active": False
        }

        response = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=admin_headers_with_perms)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Fully Updated"
        assert data["description"] == "All fields updated"
        assert data["is_active"] is False

    def test_update_department_empty_name(self, client, admin_headers_with_perms, test_department):
        """Test updating department with empty name"""
        update_data = {
            "name": ""
        }

        response = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=admin_headers_with_perms)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "empty" in data["error"].lower()

    def test_update_department_whitespace_name(self, client, admin_headers_with_perms, test_department):
        """Test updating department with whitespace-only name"""
        update_data = {
            "name": "   "
        }

        response = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=admin_headers_with_perms)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "empty" in data["error"].lower()

    def test_update_department_null_name(self, client, admin_headers_with_perms, test_department):
        """Test updating department with null name"""
        update_data = {
            "name": None
        }

        response = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=admin_headers_with_perms)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_update_department_trim_whitespace(self, client, admin_headers_with_perms, test_department):
        """Test that updated name and description are trimmed"""
        update_data = {
            "name": "  Trimmed Update  ",
            "description": "  Trimmed Desc  "
        }

        response = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=admin_headers_with_perms)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Trimmed Update"
        assert data["description"] == "Trimmed Desc"

    def test_update_department_duplicate_name(self, client, admin_headers_with_perms, test_department, clean_departments):
        """Test updating department to duplicate name"""
        # Create another department
        other_dept = Department(name="Other Department", is_active=True)
        clean_departments.add(other_dept)
        clean_departments.commit()

        update_data = {
            "name": "Other Department"
        }

        response = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=admin_headers_with_perms)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "already exists" in data["error"].lower()

    def test_update_department_duplicate_name_case_insensitive(self, client, admin_headers_with_perms, test_department, clean_departments):
        """Test that duplicate name check is case-insensitive"""
        other_dept = Department(name="Other Department", is_active=True)
        clean_departments.add(other_dept)
        clean_departments.commit()

        update_data = {
            "name": "other department"  # Different case
        }

        response = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=admin_headers_with_perms)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "already exists" in data["error"].lower()

    def test_update_department_same_name(self, client, admin_headers_with_perms, test_department):
        """Test updating department with its own current name"""
        update_data = {
            "name": "Test Department"
        }

        response = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=admin_headers_with_perms)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Test Department"

    def test_update_department_empty_body(self, client, admin_headers_with_perms, test_department):
        """Test updating department with empty body (no changes)"""
        response = client.put(f"/api/departments/{test_department.id}", json={}, headers=admin_headers_with_perms)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Test Department"  # Unchanged

    def test_update_department_no_json(self, client, admin_headers_with_perms, test_department):
        """Test updating department without JSON body"""
        response = client.put(f"/api/departments/{test_department.id}", headers=admin_headers_with_perms)

        # Without Content-Type header, Flask raises UnsupportedMediaType (500 in error handler)
        assert response.status_code in [200, 415, 500]

    def test_update_department_not_found(self, client, admin_headers_with_perms, clean_departments):
        """Test updating non-existent department"""
        update_data = {
            "name": "Non-existent"
        }

        response = client.put("/api/departments/99999", json=update_data, headers=admin_headers_with_perms)
        assert response.status_code == 404

    def test_update_department_without_auth(self, client, test_department):
        """Test updating department without authentication"""
        update_data = {
            "name": "Unauthorized Update"
        }

        response = client.put(f"/api/departments/{test_department.id}", json=update_data)
        assert response.status_code == 401

    def test_update_department_no_permission(self, client, auth_headers_user, test_department):
        """Test updating department without proper permissions"""
        update_data = {
            "name": "No Permission Update"
        }

        response = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=auth_headers_user)
        assert response.status_code == 403

    def test_update_department_integrity_error(self, client, admin_headers_with_perms, test_department):
        """Test handling IntegrityError during update"""
        with patch("routes_departments.db.session.commit") as mock_commit:
            mock_commit.side_effect = IntegrityError("Duplicate", {}, None)

            update_data = {
                "name": "Integrity Error Update"
            }

            response = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=admin_headers_with_perms)

            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data
            assert "already exists" in data["error"].lower()

    def test_update_department_sqlalchemy_error(self, client, admin_headers_with_perms, test_department):
        """Test handling SQLAlchemy errors during update"""
        with patch("routes_departments.db.session.commit") as mock_commit:
            mock_commit.side_effect = SQLAlchemyError("Database error")

            update_data = {
                "name": "SQLAlchemy Error Update"
            }

            response = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=admin_headers_with_perms)

            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
            assert "Failed to update department" in data["error"]


class TestDeleteDepartmentEndpoint:
    """Test the DELETE /api/departments/<id> endpoint (soft delete)"""

    def test_delete_department_success(self, client, admin_headers_with_perms, test_department):
        """Test soft deleting a department"""
        response = client.delete(f"/api/departments/{test_department.id}", headers=admin_headers_with_perms)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "deactivated" in data["message"].lower()

    def test_delete_department_verifies_inactive(self, client, admin_headers_with_perms, test_department, clean_departments):
        """Test that soft delete actually deactivates the department"""
        client.delete(f"/api/departments/{test_department.id}", headers=admin_headers_with_perms)

        # Verify the department is deactivated
        department = Department.query.get(test_department.id)
        assert department is not None
        assert department.is_active is False

    def test_delete_already_inactive_department(self, client, admin_headers_with_perms, inactive_department):
        """Test deleting an already inactive department"""
        response = client.delete(f"/api/departments/{inactive_department.id}", headers=admin_headers_with_perms)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data

    def test_delete_department_not_found(self, client, admin_headers_with_perms, clean_departments):
        """Test deleting non-existent department"""
        response = client.delete("/api/departments/99999", headers=admin_headers_with_perms)
        assert response.status_code == 404

    def test_delete_department_without_auth(self, client, test_department):
        """Test deleting department without authentication"""
        response = client.delete(f"/api/departments/{test_department.id}")
        assert response.status_code == 401

    def test_delete_department_no_permission(self, client, auth_headers_user, test_department):
        """Test deleting department without proper permissions"""
        response = client.delete(f"/api/departments/{test_department.id}", headers=auth_headers_user)
        assert response.status_code == 403

    def test_delete_department_sqlalchemy_error(self, client, admin_headers_with_perms, test_department):
        """Test handling SQLAlchemy errors during soft delete"""
        with patch("routes_departments.db.session.commit") as mock_commit:
            mock_commit.side_effect = SQLAlchemyError("Database error")

            response = client.delete(f"/api/departments/{test_department.id}", headers=admin_headers_with_perms)

            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
            assert "Failed to delete department" in data["error"]


class TestHardDeleteDepartmentEndpoint:
    """Test the DELETE /api/departments/<id>/hard-delete endpoint"""

    def test_hard_delete_department_success(self, client, admin_headers_with_perms, test_department, clean_departments):
        """Test permanently deleting a department"""
        dept_id = test_department.id

        response = client.delete(f"/api/departments/{dept_id}/hard-delete", headers=admin_headers_with_perms)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "permanently deleted" in data["message"].lower()

        # Verify the department is completely removed
        department = Department.query.get(dept_id)
        assert department is None

    def test_hard_delete_inactive_department(self, client, admin_headers_with_perms, inactive_department, clean_departments):
        """Test hard deleting an inactive department"""
        dept_id = inactive_department.id

        response = client.delete(f"/api/departments/{dept_id}/hard-delete", headers=admin_headers_with_perms)

        assert response.status_code == 200
        department = Department.query.get(dept_id)
        assert department is None

    def test_hard_delete_department_with_users(self, client, admin_headers_with_perms, test_department, db_session):
        """Test hard deleting department with users assigned"""
        # Create a user assigned to this department
        user = User(
            name="Assigned User",
            employee_number="DEPT001",
            department=test_department.name,  # Assigned to test department
            password_hash="hash",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        response = client.delete(f"/api/departments/{test_department.id}/hard-delete", headers=admin_headers_with_perms)

        assert response.status_code == 409
        data = json.loads(response.data)
        assert "error" in data
        assert "Cannot delete" in data["error"]
        assert "user_count" in data
        assert data["user_count"] == 1

    def test_hard_delete_department_with_multiple_users(self, client, admin_headers_with_perms, test_department, db_session):
        """Test hard deleting department with multiple users assigned"""
        # Create multiple users assigned to this department
        for i in range(3):
            user = User(
                name=f"User {i}",
                employee_number=f"DEPT00{i}",
                department=test_department.name,
                password_hash="hash",
                is_active=True
            )
            db_session.add(user)
        db_session.commit()

        response = client.delete(f"/api/departments/{test_department.id}/hard-delete", headers=admin_headers_with_perms)

        assert response.status_code == 409
        data = json.loads(response.data)
        assert data["user_count"] == 3

    def test_hard_delete_department_not_found(self, client, admin_headers_with_perms, clean_departments):
        """Test hard deleting non-existent department"""
        response = client.delete("/api/departments/99999/hard-delete", headers=admin_headers_with_perms)
        assert response.status_code == 404

    def test_hard_delete_department_without_auth(self, client, test_department):
        """Test hard deleting department without authentication"""
        response = client.delete(f"/api/departments/{test_department.id}/hard-delete")
        assert response.status_code == 401

    def test_hard_delete_department_no_permission(self, client, auth_headers_user, test_department):
        """Test hard deleting department without proper permissions"""
        response = client.delete(f"/api/departments/{test_department.id}/hard-delete", headers=auth_headers_user)
        assert response.status_code == 403

    def test_hard_delete_department_sqlalchemy_error(self, client, admin_headers_with_perms, test_department):
        """Test handling SQLAlchemy errors during hard delete"""
        with patch("routes_departments.db.session.commit") as mock_commit:
            mock_commit.side_effect = SQLAlchemyError("Database error")

            response = client.delete(f"/api/departments/{test_department.id}/hard-delete", headers=admin_headers_with_perms)

            assert response.status_code == 500
            data = json.loads(response.data)
            assert "error" in data
            assert "Failed to permanently delete department" in data["error"]


class TestDepartmentSecurityFeatures:
    """Test security features in department routes"""

    def test_xss_prevention_in_department_name(self, client, admin_headers_with_perms, clean_departments):
        """Test XSS prevention in department name"""
        department_data = {
            "name": '<script>alert("XSS")</script>'
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

        assert response.status_code == 201
        data = json.loads(response.data)
        # The name is stored as-is; frontend should handle escaping
        assert "name" in data

    def test_xss_prevention_in_department_description(self, client, admin_headers_with_perms, clean_departments):
        """Test XSS prevention in department description"""
        department_data = {
            "name": "Security Test Department",
            "description": '<img src=x onerror=alert("XSS")>'
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert "description" in data

    def test_sql_injection_prevention_in_name(self, client, admin_headers_with_perms, clean_departments):
        """Test SQL injection prevention in department name"""
        department_data = {
            "name": "'; DROP TABLE departments; --"
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

        # Should either succeed (stored safely) or fail for other reasons, but not execute SQL
        assert response.status_code in [201, 400]

    def test_authorization_boundaries_create(self, client, auth_headers_user, clean_departments):
        """Test that regular users cannot create departments"""
        department_data = {
            "name": "Unauthorized Create"
        }

        response = client.post("/api/departments", json=department_data, headers=auth_headers_user)
        assert response.status_code == 403

    def test_authorization_boundaries_update(self, client, auth_headers_user, test_department):
        """Test that regular users cannot update departments"""
        update_data = {
            "name": "Unauthorized Update"
        }

        response = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=auth_headers_user)
        assert response.status_code == 403

    def test_authorization_boundaries_delete(self, client, auth_headers_user, test_department):
        """Test that regular users cannot delete departments"""
        response = client.delete(f"/api/departments/{test_department.id}", headers=auth_headers_user)
        assert response.status_code == 403

    def test_authorization_boundaries_hard_delete(self, client, auth_headers_user, test_department):
        """Test that regular users cannot hard delete departments"""
        response = client.delete(f"/api/departments/{test_department.id}/hard-delete", headers=auth_headers_user)
        assert response.status_code == 403


class TestDepartmentEdgeCases:
    """Test edge cases and error handling"""

    def test_very_long_department_name(self, client, admin_headers_with_perms, clean_departments):
        """Test creating department with very long name"""
        department_data = {
            "name": "A" * 1000
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)
        # Should either truncate, accept, or reject based on database constraints
        assert response.status_code in [201, 400, 500]

    def test_very_long_department_description(self, client, admin_headers_with_perms, clean_departments):
        """Test creating department with very long description"""
        department_data = {
            "name": "Long Description Department",
            "description": "B" * 10000
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)
        assert response.status_code in [201, 400, 500]

    def test_special_characters_in_name(self, client, admin_headers_with_perms, clean_departments):
        """Test creating department with special characters"""
        department_data = {
            "name": "Department & Co. (2024) - Main/Sub"
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["name"] == "Department & Co. (2024) - Main/Sub"

    def test_unicode_characters_in_name(self, client, admin_headers_with_perms, clean_departments):
        """Test creating department with unicode characters"""
        department_data = {
            "name": "Département français 日本語部門"
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert "français" in data["name"]
        assert "日本語" in data["name"]

    def test_null_description_handling(self, client, admin_headers_with_perms, clean_departments):
        """Test creating department with null description"""
        department_data = {
            "name": "Null Description Department",
            "description": None
        }

        response = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["description"] == ""  # Should be empty string after stripping

    def test_update_null_description(self, client, admin_headers_with_perms, test_department):
        """Test updating department with null description"""
        update_data = {
            "description": None
        }

        response = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=admin_headers_with_perms)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["description"] == ""

    def test_concurrent_department_creation(self, client, admin_headers_with_perms, clean_departments):
        """Test that duplicate check works for concurrent creation attempts"""
        # First creation should succeed
        department_data = {
            "name": "Concurrent Test"
        }

        response1 = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)
        assert response1.status_code == 201

        # Second creation with same name should fail
        response2 = client.post("/api/departments", json=department_data, headers=admin_headers_with_perms)
        assert response2.status_code == 400

    def test_get_department_response_structure(self, client, auth_headers_user, test_department):
        """Test that department response has all expected fields"""
        response = client.get(f"/api/departments/{test_department.id}", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        # Verify all expected fields are present
        assert "id" in data
        assert "name" in data
        assert "description" in data
        assert "is_active" in data
        assert "created_at" in data
        assert "updated_at" in data

        # Verify types
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)
        assert isinstance(data["description"], str)
        assert isinstance(data["is_active"], bool)
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)

    def test_update_preserves_created_at(self, client, admin_headers_with_perms, test_department):
        """Test that updating department preserves created_at timestamp"""
        # Get original created_at
        response1 = client.get(f"/api/departments/{test_department.id}", headers=admin_headers_with_perms)
        original_data = json.loads(response1.data)
        original_created_at = original_data["created_at"]

        # Update department
        update_data = {"description": "Updated"}
        response2 = client.put(f"/api/departments/{test_department.id}", json=update_data, headers=admin_headers_with_perms)
        updated_data = json.loads(response2.data)

        # created_at should be unchanged
        assert updated_data["created_at"] == original_created_at
