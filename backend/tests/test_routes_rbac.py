"""
Comprehensive tests for routes_rbac.py - Role-Based Access Control endpoints
"""

import pytest
from werkzeug.security import generate_password_hash

from models import AuditLog, Permission, Role, RolePermission, User, UserRole, db
from auth import JWTManager


@pytest.fixture
def rbac_user_with_role_manage(db_session):
    """Create a user with role.manage permission"""
    # Create permission
    permission = Permission(
        name="role.manage",
        description="Manage roles",
        category="Administration"
    )
    db_session.add(permission)
    db_session.flush()

    # Create role
    role = Role(
        name="Role Manager",
        description="Can manage roles",
        is_system_role=False
    )
    db_session.add(role)
    db_session.flush()

    # Assign permission to role
    role_perm = RolePermission(role_id=role.id, permission_id=permission.id)
    db_session.add(role_perm)

    # Create user
    user = User(
        name="Role Manager User",
        employee_number="RBAC001",
        department="IT",
        password_hash=generate_password_hash("password123"),
        is_admin=False,
        is_active=True
    )
    db_session.add(user)
    db_session.flush()

    # Assign role to user
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    db_session.commit()

    return user


@pytest.fixture
def rbac_user_with_user_permissions(db_session):
    """Create a user with user.view and user.edit permissions"""
    # Create permissions
    view_perm = Permission(
        name="user.view",
        description="View users",
        category="User Management"
    )
    edit_perm = Permission(
        name="user.edit",
        description="Edit users",
        category="User Management"
    )
    db_session.add(view_perm)
    db_session.add(edit_perm)
    db_session.flush()

    # Create role
    role = Role(
        name="User Manager",
        description="Can manage users",
        is_system_role=False
    )
    db_session.add(role)
    db_session.flush()

    # Assign permissions to role
    role_perm1 = RolePermission(role_id=role.id, permission_id=view_perm.id)
    role_perm2 = RolePermission(role_id=role.id, permission_id=edit_perm.id)
    db_session.add(role_perm1)
    db_session.add(role_perm2)

    # Create user
    user = User(
        name="User Manager",
        employee_number="USERMGR001",
        department="HR",
        password_hash=generate_password_hash("password123"),
        is_admin=False,
        is_active=True
    )
    db_session.add(user)
    db_session.flush()

    # Assign role to user
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db_session.add(user_role)
    db_session.commit()

    return user


@pytest.fixture
def rbac_token(app, rbac_user_with_role_manage):
    """Generate JWT token for RBAC user"""
    with app.app_context():
        tokens = JWTManager.generate_tokens(rbac_user_with_role_manage)
        return tokens["access_token"]


@pytest.fixture
def user_manager_token(app, rbac_user_with_user_permissions):
    """Generate JWT token for user manager"""
    with app.app_context():
        tokens = JWTManager.generate_tokens(rbac_user_with_user_permissions)
        return tokens["access_token"]


@pytest.fixture
def auth_headers_rbac(rbac_token):
    """Create authorization headers for RBAC user"""
    return {"Authorization": f"Bearer {rbac_token}"}


@pytest.fixture
def auth_headers_user_manager(user_manager_token):
    """Create authorization headers for user manager"""
    return {"Authorization": f"Bearer {user_manager_token}"}


@pytest.fixture
def sample_permissions(db_session):
    """Create sample permissions for testing"""
    permissions = [
        Permission(name="tool.view", description="View tools", category="Tools"),
        Permission(name="tool.edit", description="Edit tools", category="Tools"),
        Permission(name="chemical.view", description="View chemicals", category="Chemicals"),
        Permission(name="chemical.edit", description="Edit chemicals", category="Chemicals"),
        Permission(name="uncategorized_perm", description="No category", category=None),
    ]
    for perm in permissions:
        db_session.add(perm)
    db_session.commit()
    return permissions


@pytest.fixture
def sample_roles(db_session):
    """Create sample roles for testing"""
    roles = [
        Role(name="Admin", description="Administrator role", is_system_role=True),
        Role(name="User", description="Regular user role", is_system_role=False),
        Role(name="Manager", description="Manager role", is_system_role=False),
    ]
    for role in roles:
        db_session.add(role)
    db_session.commit()
    return roles


class TestGetRoles:
    """Tests for GET /api/roles endpoint"""

    def test_get_roles_success(self, client, auth_headers_rbac, sample_roles):
        """Test successfully retrieving all roles"""
        response = client.get("/api/roles", headers=auth_headers_rbac)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # Should include sample roles plus the Role Manager role from fixture
        assert len(data) >= 3

    def test_get_roles_empty(self, client, auth_headers_rbac):
        """Test retrieving roles when only the fixture role exists"""
        response = client.get("/api/roles", headers=auth_headers_rbac)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # At least the Role Manager role exists
        assert len(data) >= 1

    def test_get_roles_without_permission(self, client, auth_headers_user):
        """Test that user without role.manage permission cannot access roles"""
        response = client.get("/api/roles", headers=auth_headers_user)
        assert response.status_code == 403

    def test_get_roles_without_auth(self, client):
        """Test that unauthenticated request is rejected"""
        response = client.get("/api/roles")
        assert response.status_code == 401


class TestGetRole:
    """Tests for GET /api/roles/<id> endpoint"""

    def test_get_role_success(self, client, auth_headers_rbac, sample_roles):
        """Test successfully retrieving a specific role"""
        role_id = sample_roles[0].id
        response = client.get(f"/api/roles/{role_id}", headers=auth_headers_rbac)
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == role_id
        assert data["name"] == "Admin"
        assert "permissions" in data

    def test_get_role_with_permissions(self, client, auth_headers_rbac, sample_roles, sample_permissions):
        """Test retrieving role with its permissions"""
        role = sample_roles[1]  # User role
        # Add permissions to role
        role_perm = RolePermission(role_id=role.id, permission_id=sample_permissions[0].id)
        db.session.add(role_perm)
        db.session.commit()

        response = client.get(f"/api/roles/{role.id}", headers=auth_headers_rbac)
        assert response.status_code == 200
        data = response.get_json()
        assert "permissions" in data
        assert len(data["permissions"]) == 1
        assert data["permissions"][0]["name"] == "tool.view"

    def test_get_role_not_found(self, client, auth_headers_rbac):
        """Test retrieving non-existent role"""
        response = client.get("/api/roles/99999", headers=auth_headers_rbac)
        assert response.status_code == 404

    def test_get_role_without_permission(self, client, auth_headers_user, sample_roles):
        """Test that user without role.manage permission cannot access role"""
        role_id = sample_roles[0].id
        response = client.get(f"/api/roles/{role_id}", headers=auth_headers_user)
        assert response.status_code == 403


class TestCreateRole:
    """Tests for POST /api/roles endpoint"""

    def test_create_role_success(self, client, auth_headers_rbac):
        """Test successfully creating a new role"""
        data = {
            "name": "Test Role",
            "description": "A test role"
        }
        response = client.post("/api/roles", json=data, headers=auth_headers_rbac)
        assert response.status_code == 201
        result = response.get_json()
        assert result["name"] == "Test Role"
        assert result["description"] == "A test role"
        assert result["is_system_role"] is False
        assert "permissions" in result

        # Verify audit log
        log = AuditLog.query.filter_by(action_type="create_role").first()
        assert log is not None
        assert "Test Role" in log.action_details

    def test_create_role_with_permissions(self, client, auth_headers_rbac, sample_permissions):
        """Test creating role with permissions"""
        permission_ids = [sample_permissions[0].id, sample_permissions[1].id]
        data = {
            "name": "Role With Perms",
            "description": "Has permissions",
            "permissions": permission_ids
        }
        response = client.post("/api/roles", json=data, headers=auth_headers_rbac)
        assert response.status_code == 201
        result = response.get_json()
        assert len(result["permissions"]) == 2

    def test_create_role_with_invalid_permissions(self, client, auth_headers_rbac):
        """Test creating role with non-existent permission IDs"""
        data = {
            "name": "Role With Bad Perms",
            "description": "Invalid permissions",
            "permissions": [99999, 99998]
        }
        response = client.post("/api/roles", json=data, headers=auth_headers_rbac)
        # Should still create role but ignore invalid permission IDs
        assert response.status_code == 201
        result = response.get_json()
        assert len(result["permissions"]) == 0

    def test_create_role_missing_name(self, client, auth_headers_rbac):
        """Test creating role without name"""
        data = {
            "description": "Missing name"
        }
        response = client.post("/api/roles", json=data, headers=auth_headers_rbac)
        assert response.status_code == 400
        assert "Role name is required" in response.get_json()["error"]

    def test_create_role_empty_name(self, client, auth_headers_rbac):
        """Test creating role with empty name"""
        data = {
            "name": "",
            "description": "Empty name"
        }
        response = client.post("/api/roles", json=data, headers=auth_headers_rbac)
        assert response.status_code == 400
        assert "Role name is required" in response.get_json()["error"]

    def test_create_role_duplicate_name(self, client, auth_headers_rbac, sample_roles):
        """Test creating role with duplicate name"""
        data = {
            "name": "Admin",  # Already exists
            "description": "Duplicate"
        }
        response = client.post("/api/roles", json=data, headers=auth_headers_rbac)
        assert response.status_code == 400
        assert "already exists" in response.get_json()["error"]

    def test_create_role_without_permission(self, client, auth_headers_user):
        """Test that user without role.manage permission cannot create role"""
        data = {
            "name": "Unauthorized Role",
            "description": "Should fail"
        }
        response = client.post("/api/roles", json=data, headers=auth_headers_user)
        assert response.status_code == 403

    def test_create_role_no_json_body(self, client, auth_headers_rbac):
        """Test creating role without JSON body results in server error"""
        response = client.post("/api/roles", headers=auth_headers_rbac)
        # Flask raises 415 Unsupported Media Type when no Content-Type is set
        assert response.status_code == 500

    def test_create_role_default_description(self, client, auth_headers_rbac):
        """Test creating role without description uses empty string"""
        data = {
            "name": "No Description Role"
        }
        response = client.post("/api/roles", json=data, headers=auth_headers_rbac)
        assert response.status_code == 201
        result = response.get_json()
        assert result["description"] == ""


class TestUpdateRole:
    """Tests for PUT /api/roles/<id> endpoint"""

    def test_update_role_name(self, client, auth_headers_rbac, sample_roles):
        """Test updating role name"""
        role = sample_roles[1]  # Non-system role
        data = {
            "name": "Updated Name"
        }
        response = client.put(f"/api/roles/{role.id}", json=data, headers=auth_headers_rbac)
        assert response.status_code == 200
        result = response.get_json()
        assert result["name"] == "Updated Name"

        # Verify audit log
        log = AuditLog.query.filter_by(action_type="update_role").first()
        assert log is not None

    def test_update_role_description(self, client, auth_headers_rbac, sample_roles):
        """Test updating role description"""
        role = sample_roles[1]  # Non-system role
        data = {
            "description": "Updated description"
        }
        response = client.put(f"/api/roles/{role.id}", json=data, headers=auth_headers_rbac)
        assert response.status_code == 200
        result = response.get_json()
        assert result["description"] == "Updated description"

    def test_update_role_permissions(self, client, auth_headers_rbac, sample_roles, sample_permissions):
        """Test updating role permissions"""
        role = sample_roles[1]  # Non-system role
        permission_ids = [sample_permissions[0].id, sample_permissions[2].id]
        data = {
            "permissions": permission_ids
        }
        response = client.put(f"/api/roles/{role.id}", json=data, headers=auth_headers_rbac)
        assert response.status_code == 200
        result = response.get_json()
        assert len(result["permissions"]) == 2

    def test_update_role_replace_permissions(self, client, auth_headers_rbac, sample_roles, sample_permissions):
        """Test that updating permissions replaces existing ones"""
        role = sample_roles[1]  # Non-system role
        # First add some permissions
        role_perm = RolePermission(role_id=role.id, permission_id=sample_permissions[0].id)
        db.session.add(role_perm)
        db.session.commit()

        # Now update to different permissions
        data = {
            "permissions": [sample_permissions[2].id]
        }
        response = client.put(f"/api/roles/{role.id}", json=data, headers=auth_headers_rbac)
        assert response.status_code == 200
        result = response.get_json()
        assert len(result["permissions"]) == 1
        assert result["permissions"][0]["name"] == "chemical.view"

    def test_update_role_duplicate_name(self, client, auth_headers_rbac, sample_roles):
        """Test updating role name to duplicate"""
        role = sample_roles[1]  # User role
        data = {
            "name": "Admin"  # Already exists
        }
        response = client.put(f"/api/roles/{role.id}", json=data, headers=auth_headers_rbac)
        assert response.status_code == 400
        assert "already exists" in response.get_json()["error"]

    def test_update_role_same_name(self, client, auth_headers_rbac, sample_roles):
        """Test updating role with same name is allowed"""
        role = sample_roles[1]  # User role
        data = {
            "name": "User",  # Same name
            "description": "Updated desc"
        }
        response = client.put(f"/api/roles/{role.id}", json=data, headers=auth_headers_rbac)
        assert response.status_code == 200

    def test_update_system_role_name_forbidden(self, client, auth_headers_rbac, sample_roles):
        """Test that system role name cannot be updated"""
        role = sample_roles[0]  # System role
        data = {
            "name": "New Name"
        }
        response = client.put(f"/api/roles/{role.id}", json=data, headers=auth_headers_rbac)
        assert response.status_code == 403
        assert "System role" in response.get_json()["error"]

    def test_update_system_role_description_forbidden(self, client, auth_headers_rbac, sample_roles):
        """Test that system role description cannot be updated"""
        role = sample_roles[0]  # System role
        data = {
            "description": "New Description"
        }
        response = client.put(f"/api/roles/{role.id}", json=data, headers=auth_headers_rbac)
        assert response.status_code == 403
        assert "System role" in response.get_json()["error"]

    def test_update_system_role_permissions_allowed(self, client, auth_headers_rbac, sample_roles, sample_permissions):
        """Test that system role permissions can be updated"""
        role = sample_roles[0]  # System role
        data = {
            "permissions": [sample_permissions[0].id]
        }
        response = client.put(f"/api/roles/{role.id}", json=data, headers=auth_headers_rbac)
        assert response.status_code == 200
        result = response.get_json()
        assert len(result["permissions"]) == 1

    def test_update_role_not_found(self, client, auth_headers_rbac):
        """Test updating non-existent role"""
        data = {
            "name": "New Name"
        }
        response = client.put("/api/roles/99999", json=data, headers=auth_headers_rbac)
        assert response.status_code == 404

    def test_update_role_without_permission(self, client, auth_headers_user, sample_roles):
        """Test that user without role.manage permission cannot update role"""
        role = sample_roles[1]
        data = {
            "name": "Unauthorized Update"
        }
        response = client.put(f"/api/roles/{role.id}", json=data, headers=auth_headers_user)
        assert response.status_code == 403

    def test_update_role_with_invalid_permission_ids(self, client, auth_headers_rbac, sample_roles):
        """Test updating role with invalid permission IDs"""
        role = sample_roles[1]
        data = {
            "permissions": [99999]
        }
        response = client.put(f"/api/roles/{role.id}", json=data, headers=auth_headers_rbac)
        assert response.status_code == 200
        result = response.get_json()
        assert len(result["permissions"]) == 0

    def test_update_role_no_json_body(self, client, auth_headers_rbac, sample_roles):
        """Test updating role without JSON body results in server error"""
        role = sample_roles[1]
        response = client.put(f"/api/roles/{role.id}", headers=auth_headers_rbac)
        # Flask raises 415 Unsupported Media Type when no Content-Type is set
        assert response.status_code == 500


class TestDeleteRole:
    """Tests for DELETE /api/roles/<id> endpoint"""

    def test_delete_role_success(self, client, auth_headers_rbac, sample_roles):
        """Test successfully deleting a role"""
        role = sample_roles[1]  # Non-system role
        role_id = role.id
        response = client.delete(f"/api/roles/{role_id}", headers=auth_headers_rbac)
        assert response.status_code == 200
        assert "deleted successfully" in response.get_json()["message"]

        # Verify role is deleted
        assert Role.query.get(role_id) is None

        # Verify audit log
        log = AuditLog.query.filter_by(action_type="delete_role").first()
        assert log is not None

    def test_delete_role_with_permissions(self, client, auth_headers_rbac, sample_roles, sample_permissions):
        """Test deleting role removes its permission associations"""
        role = sample_roles[1]  # Non-system role
        role_perm = RolePermission(role_id=role.id, permission_id=sample_permissions[0].id)
        db.session.add(role_perm)
        db.session.commit()

        role_id = role.id
        response = client.delete(f"/api/roles/{role_id}", headers=auth_headers_rbac)
        assert response.status_code == 200

        # Verify permissions associations are removed
        assert RolePermission.query.filter_by(role_id=role_id).count() == 0

    def test_delete_role_with_users(self, client, auth_headers_rbac, sample_roles, regular_user):
        """Test deleting role removes user associations"""
        role = sample_roles[1]  # Non-system role
        user_role = UserRole(user_id=regular_user.id, role_id=role.id)
        db.session.add(user_role)
        db.session.commit()

        role_id = role.id
        response = client.delete(f"/api/roles/{role_id}", headers=auth_headers_rbac)
        assert response.status_code == 200

        # Verify user associations are removed
        assert UserRole.query.filter_by(role_id=role_id).count() == 0

    def test_delete_system_role_forbidden(self, client, auth_headers_rbac, sample_roles):
        """Test that system roles cannot be deleted"""
        role = sample_roles[0]  # System role
        response = client.delete(f"/api/roles/{role.id}", headers=auth_headers_rbac)
        assert response.status_code == 403
        assert "System roles cannot be deleted" in response.get_json()["error"]

    def test_delete_role_not_found(self, client, auth_headers_rbac):
        """Test deleting non-existent role"""
        response = client.delete("/api/roles/99999", headers=auth_headers_rbac)
        assert response.status_code == 404

    def test_delete_role_without_permission(self, client, auth_headers_user, sample_roles):
        """Test that user without role.manage permission cannot delete role"""
        role = sample_roles[1]
        response = client.delete(f"/api/roles/{role.id}", headers=auth_headers_user)
        assert response.status_code == 403


class TestGetPermissions:
    """Tests for GET /api/permissions endpoint"""

    def test_get_permissions_success(self, client, auth_headers_rbac, sample_permissions):
        """Test successfully retrieving all permissions"""
        response = client.get("/api/permissions", headers=auth_headers_rbac)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # Should include sample permissions plus role.manage from fixture
        assert len(data) >= 5

    def test_get_permissions_empty(self, client, auth_headers_rbac):
        """Test retrieving permissions when only fixture permission exists"""
        response = client.get("/api/permissions", headers=auth_headers_rbac)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # At least role.manage exists
        assert len(data) >= 1

    def test_get_permissions_without_permission(self, client, auth_headers_user):
        """Test that user without role.manage permission cannot access permissions"""
        response = client.get("/api/permissions", headers=auth_headers_user)
        assert response.status_code == 403

    def test_get_permissions_structure(self, client, auth_headers_rbac, sample_permissions):
        """Test that permissions have correct structure"""
        response = client.get("/api/permissions", headers=auth_headers_rbac)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) > 0
        perm = data[0]
        assert "id" in perm
        assert "name" in perm
        assert "description" in perm
        assert "category" in perm
        assert "created_at" in perm


class TestGetPermissionsByCategory:
    """Tests for GET /api/permissions/categories endpoint"""

    def test_get_permissions_by_category_success(self, client, auth_headers_rbac, sample_permissions):
        """Test successfully retrieving permissions grouped by category"""
        response = client.get("/api/permissions/categories", headers=auth_headers_rbac)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert "Tools" in data
        assert "Chemicals" in data
        assert len(data["Tools"]) == 2
        assert len(data["Chemicals"]) == 2

    def test_get_permissions_uncategorized(self, client, auth_headers_rbac, sample_permissions):
        """Test that permissions without category are grouped as Uncategorized"""
        response = client.get("/api/permissions/categories", headers=auth_headers_rbac)
        assert response.status_code == 200
        data = response.get_json()
        assert "Uncategorized" in data
        uncategorized = [p for p in data["Uncategorized"] if p["name"] == "uncategorized_perm"]
        assert len(uncategorized) == 1

    def test_get_permissions_by_category_empty(self, client, auth_headers_rbac):
        """Test retrieving categories when only fixture permission exists"""
        response = client.get("/api/permissions/categories", headers=auth_headers_rbac)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        # At least Administration category exists from fixture
        assert "Administration" in data

    def test_get_permissions_by_category_without_permission(self, client, auth_headers_user):
        """Test that user without role.manage permission cannot access categories"""
        response = client.get("/api/permissions/categories", headers=auth_headers_user)
        assert response.status_code == 403


class TestGetUserRoles:
    """Tests for GET /api/users/<user_id>/roles endpoint"""

    def test_get_user_roles_success(self, client, auth_headers_user_manager, rbac_user_with_role_manage):
        """Test successfully retrieving user roles"""
        user_id = rbac_user_with_role_manage.id
        response = client.get(f"/api/users/{user_id}/roles", headers=auth_headers_user_manager)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["name"] == "Role Manager"

    def test_get_user_roles_empty(self, client, auth_headers_user_manager, regular_user):
        """Test retrieving roles for user with no roles"""
        response = client.get(f"/api/users/{regular_user.id}/roles", headers=auth_headers_user_manager)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_user_roles_not_found(self, client, auth_headers_user_manager):
        """Test retrieving roles for non-existent user"""
        response = client.get("/api/users/99999/roles", headers=auth_headers_user_manager)
        assert response.status_code == 404

    def test_get_user_roles_without_permission(self, client, auth_headers_user, regular_user):
        """Test that user without user.view permission cannot access user roles"""
        response = client.get(f"/api/users/{regular_user.id}/roles", headers=auth_headers_user)
        assert response.status_code == 403

    def test_get_user_roles_multiple_roles(self, client, auth_headers_user_manager, regular_user, sample_roles):
        """Test retrieving multiple roles for a user"""
        # Assign multiple roles to user
        for role in sample_roles[:2]:
            user_role = UserRole(user_id=regular_user.id, role_id=role.id)
            db.session.add(user_role)
        db.session.commit()

        response = client.get(f"/api/users/{regular_user.id}/roles", headers=auth_headers_user_manager)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2


class TestUpdateUserRoles:
    """Tests for PUT /api/users/<user_id>/roles endpoint"""

    def test_update_user_roles_success(self, client, auth_headers_user_manager, regular_user, sample_roles):
        """Test successfully updating user roles"""
        role_ids = [sample_roles[0].id, sample_roles[1].id]
        data = {
            "roles": role_ids
        }
        response = client.put(f"/api/users/{regular_user.id}/roles", json=data, headers=auth_headers_user_manager)
        assert response.status_code == 200
        result = response.get_json()
        assert len(result) == 2

        # Verify audit log
        log = AuditLog.query.filter_by(action_type="update_user_roles").first()
        assert log is not None
        assert str(regular_user.id) in log.action_details

    def test_update_user_roles_replace_existing(self, client, auth_headers_user_manager, regular_user, sample_roles):
        """Test that updating roles replaces existing ones"""
        # First assign some roles
        user_role = UserRole(user_id=regular_user.id, role_id=sample_roles[0].id)
        db.session.add(user_role)
        db.session.commit()

        # Now update to different roles
        data = {
            "roles": [sample_roles[2].id]
        }
        response = client.put(f"/api/users/{regular_user.id}/roles", json=data, headers=auth_headers_user_manager)
        assert response.status_code == 200
        result = response.get_json()
        assert len(result) == 1
        assert result[0]["name"] == "Manager"

    def test_update_user_roles_empty_list(self, client, auth_headers_user_manager, regular_user, sample_roles):
        """Test updating user to have no roles"""
        # First assign a role
        user_role = UserRole(user_id=regular_user.id, role_id=sample_roles[0].id)
        db.session.add(user_role)
        db.session.commit()

        # Now remove all roles
        data = {
            "roles": []
        }
        response = client.put(f"/api/users/{regular_user.id}/roles", json=data, headers=auth_headers_user_manager)
        assert response.status_code == 200
        result = response.get_json()
        assert len(result) == 0

    def test_update_user_roles_invalid_role_ids(self, client, auth_headers_user_manager, regular_user):
        """Test updating user with invalid role IDs"""
        data = {
            "roles": [99999, 99998]
        }
        response = client.put(f"/api/users/{regular_user.id}/roles", json=data, headers=auth_headers_user_manager)
        # Should succeed but ignore invalid role IDs
        assert response.status_code == 200
        result = response.get_json()
        assert len(result) == 0

    def test_update_user_roles_missing_roles_list(self, client, auth_headers_user_manager, regular_user):
        """Test updating user without roles list"""
        data = {}
        response = client.put(f"/api/users/{regular_user.id}/roles", json=data, headers=auth_headers_user_manager)
        assert response.status_code == 400
        assert "Roles list is required" in response.get_json()["error"]

    def test_update_user_roles_invalid_roles_format(self, client, auth_headers_user_manager, regular_user):
        """Test updating user with invalid roles format"""
        data = {
            "roles": "not a list"
        }
        response = client.put(f"/api/users/{regular_user.id}/roles", json=data, headers=auth_headers_user_manager)
        assert response.status_code == 400
        assert "Roles list is required" in response.get_json()["error"]

    def test_update_user_roles_not_found(self, client, auth_headers_user_manager, sample_roles):
        """Test updating roles for non-existent user"""
        data = {
            "roles": [sample_roles[0].id]
        }
        response = client.put("/api/users/99999/roles", json=data, headers=auth_headers_user_manager)
        assert response.status_code == 404

    def test_update_user_roles_without_permission(self, client, auth_headers_user, regular_user, sample_roles):
        """Test that user without user.edit permission cannot update user roles"""
        data = {
            "roles": [sample_roles[0].id]
        }
        response = client.put(f"/api/users/{regular_user.id}/roles", json=data, headers=auth_headers_user)
        assert response.status_code == 403


class TestGetCurrentUserPermissions:
    """Tests for GET /api/auth/permissions endpoint"""

    def test_get_current_user_permissions_success(self, client, auth_headers_rbac):
        """Test successfully retrieving current user permissions"""
        response = client.get("/api/auth/permissions", headers=auth_headers_rbac)
        assert response.status_code == 200
        data = response.get_json()
        assert "permissions" in data
        assert "roles" in data
        assert isinstance(data["permissions"], list)
        assert isinstance(data["roles"], list)
        assert "role.manage" in data["permissions"]

    def test_get_current_user_permissions_with_multiple_roles(self, client, app, db_session):
        """Test user with multiple roles gets all permissions"""
        # Create user with multiple roles
        perm1 = Permission(name="perm.one", description="First")
        perm2 = Permission(name="perm.two", description="Second")
        db_session.add(perm1)
        db_session.add(perm2)
        db_session.flush()

        role1 = Role(name="Role One", description="First role")
        role2 = Role(name="Role Two", description="Second role")
        db_session.add(role1)
        db_session.add(role2)
        db_session.flush()

        # Assign different permissions to each role
        rp1 = RolePermission(role_id=role1.id, permission_id=perm1.id)
        rp2 = RolePermission(role_id=role2.id, permission_id=perm2.id)
        db_session.add(rp1)
        db_session.add(rp2)

        user = User(
            name="Multi Role User",
            employee_number="MULTI001",
            department="IT",
            password_hash=generate_password_hash("password123"),
            is_admin=False,
            is_active=True
        )
        db_session.add(user)
        db_session.flush()

        # Assign both roles to user
        ur1 = UserRole(user_id=user.id, role_id=role1.id)
        ur2 = UserRole(user_id=user.id, role_id=role2.id)
        db_session.add(ur1)
        db_session.add(ur2)
        db_session.commit()

        # Generate token
        with app.app_context():
            tokens = JWTManager.generate_tokens(user)
            token = tokens["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/permissions", headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert "perm.one" in data["permissions"]
        assert "perm.two" in data["permissions"]
        assert len(data["roles"]) == 2

    def test_get_current_user_permissions_no_roles(self, client, auth_headers_user):
        """Test user with no roles has no permissions"""
        response = client.get("/api/auth/permissions", headers=auth_headers_user)
        assert response.status_code == 200
        data = response.get_json()
        assert data["permissions"] == []
        assert data["roles"] == []

    def test_get_current_user_permissions_without_auth(self, client):
        """Test that unauthenticated request is rejected"""
        response = client.get("/api/auth/permissions")
        assert response.status_code == 401

    def test_get_current_user_permissions_user_not_found(self, client, app, db_session):
        """Test handling when user in token doesn't exist"""
        # Create user
        user = User(
            name="Temp User",
            employee_number="TEMP001",
            department="IT",
            password_hash=generate_password_hash("password123"),
            is_admin=False,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        # Generate token
        with app.app_context():
            tokens = JWTManager.generate_tokens(user)
            token = tokens["access_token"]

        # Delete user
        db_session.delete(user)
        db_session.commit()

        # Try to get permissions
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/permissions", headers=headers)
        assert response.status_code == 404
        assert "User not found" in response.get_json()["error"]


class TestRBACIntegration:
    """Integration tests for RBAC workflows"""

    def test_full_role_lifecycle(self, client, auth_headers_rbac, sample_permissions):
        """Test complete role lifecycle: create, read, update, delete"""
        # Create
        create_data = {
            "name": "Lifecycle Role",
            "description": "Testing lifecycle",
            "permissions": [sample_permissions[0].id]
        }
        create_response = client.post("/api/roles", json=create_data, headers=auth_headers_rbac)
        assert create_response.status_code == 201
        role_id = create_response.get_json()["id"]

        # Read
        read_response = client.get(f"/api/roles/{role_id}", headers=auth_headers_rbac)
        assert read_response.status_code == 200

        # Update
        update_data = {
            "name": "Updated Lifecycle Role",
            "permissions": [sample_permissions[1].id, sample_permissions[2].id]
        }
        update_response = client.put(f"/api/roles/{role_id}", json=update_data, headers=auth_headers_rbac)
        assert update_response.status_code == 200
        assert update_response.get_json()["name"] == "Updated Lifecycle Role"
        assert len(update_response.get_json()["permissions"]) == 2

        # Delete
        delete_response = client.delete(f"/api/roles/{role_id}", headers=auth_headers_rbac)
        assert delete_response.status_code == 200

        # Verify deletion
        verify_response = client.get(f"/api/roles/{role_id}", headers=auth_headers_rbac)
        assert verify_response.status_code == 404

    def test_audit_logging_for_all_operations(self, client, auth_headers_rbac, auth_headers_user_manager,
                                               sample_roles, regular_user):
        """Test that all RBAC operations create audit logs"""
        # Clear existing logs
        AuditLog.query.delete()
        db.session.commit()

        # Create role
        create_data = {"name": "Audit Test Role", "description": "For audit testing"}
        response = client.post("/api/roles", json=create_data, headers=auth_headers_rbac)
        role_id = response.get_json()["id"]

        # Update role
        update_data = {"name": "Audit Test Role Updated"}
        client.put(f"/api/roles/{role_id}", json=update_data, headers=auth_headers_rbac)

        # Update user roles
        user_roles_data = {"roles": [sample_roles[0].id]}
        client.put(f"/api/users/{regular_user.id}/roles", json=user_roles_data, headers=auth_headers_user_manager)

        # Delete role
        client.delete(f"/api/roles/{role_id}", headers=auth_headers_rbac)

        # Verify all audit logs
        logs = AuditLog.query.all()
        action_types = [log.action_type for log in logs]
        assert "create_role" in action_types
        assert "update_role" in action_types
        assert "update_user_roles" in action_types
        assert "delete_role" in action_types
