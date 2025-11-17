"""
Comprehensive tests for routes_security.py endpoints.
Tests security settings GET and PUT endpoints with various scenarios.
"""

import pytest


class TestGetSecuritySettings:
    """Tests for GET /api/security/settings endpoint."""

    def test_get_security_settings_success_no_db_setting(self, client, auth_headers):
        """Test getting security settings when no database setting exists."""
        response = client.get("/api/security/settings", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()

        assert "session_timeout_minutes" in data
        assert "default_timeout_minutes" in data
        assert "min_timeout_minutes" in data
        assert "max_timeout_minutes" in data
        assert "source" in data
        assert "updated_at" in data
        assert "updated_by" in data

        # When no DB setting, source should be "config"
        assert data["source"] == "config"
        assert data["updated_at"] is None
        assert data["updated_by"] is None
        assert data["min_timeout_minutes"] == 5
        assert data["max_timeout_minutes"] == 240

    def test_get_security_settings_requires_authentication(self, client):
        """Test that GET endpoint requires JWT authentication."""
        response = client.get("/api/security/settings")

        assert response.status_code == 401

    def test_get_security_settings_with_invalid_token(self, client):
        """Test GET endpoint with invalid JWT token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/security/settings", headers=headers)

        assert response.status_code == 401

    def test_get_security_settings_with_db_setting(self, client, auth_headers, db_session, admin_user):
        """Test getting security settings when database setting exists."""
        from models import SystemSetting
        from utils.system_settings import SESSION_TIMEOUT_KEY

        # Create a database setting
        setting = SystemSetting(
            key=SESSION_TIMEOUT_KEY,
            value="60",
            category="security",
            description="Session timeout",
            is_sensitive=False,
            updated_by_id=admin_user.id
        )
        db_session.add(setting)
        db_session.commit()

        response = client.get("/api/security/settings", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()

        assert data["session_timeout_minutes"] == 60
        assert data["source"] == "database"
        assert data["updated_by"] is not None
        assert data["updated_by"]["id"] == admin_user.id
        assert data["updated_by"]["name"] == admin_user.name
        assert data["updated_by"]["employee_number"] == admin_user.employee_number
        assert data["updated_at"] is not None

    def test_get_security_settings_with_db_setting_no_updated_by(self, client, auth_headers, db_session):
        """Test getting security settings when setting has no updated_by user."""
        from models import SystemSetting
        from utils.system_settings import SESSION_TIMEOUT_KEY

        # Create a database setting without updated_by
        setting = SystemSetting(
            key=SESSION_TIMEOUT_KEY,
            value="45",
            category="security",
            description="Session timeout",
            is_sensitive=False,
            updated_by_id=None
        )
        db_session.add(setting)
        db_session.commit()

        response = client.get("/api/security/settings", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()

        assert data["session_timeout_minutes"] == 45
        assert data["source"] == "database"
        assert data["updated_by"] is None
        assert data["updated_at"] is not None

    def test_get_security_settings_regular_user(self, client, user_auth_headers):
        """Test that regular users can access GET endpoint."""
        response = client.get("/api/security/settings", headers=user_auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert "session_timeout_minutes" in data


class TestUpdateSecuritySettings:
    """Tests for PUT /api/security/settings endpoint."""

    @pytest.fixture
    def auth_headers_with_system_settings_permission(self, client, db_session, regular_user, jwt_manager):
        """Create auth headers for a user with system.settings permission."""
        from models import Permission, Role, RolePermission, UserRole

        # Create permission if it doesn't exist
        permission = db_session.query(Permission).filter_by(name="system.settings").first()
        if not permission:
            permission = Permission(
                name="system.settings",
                description="Manage system settings",
                category="System"
            )
            db_session.add(permission)
            db_session.flush()

        # Create role
        role = db_session.query(Role).filter_by(name="Settings Manager").first()
        if not role:
            role = Role(name="Settings Manager", description="Can manage system settings")
            db_session.add(role)
            db_session.flush()

        # Link permission to role
        role_permission = (
            db_session.query(RolePermission)
            .filter_by(role_id=role.id, permission_id=permission.id)
            .first()
        )
        if not role_permission:
            role_permission = RolePermission(role_id=role.id, permission_id=permission.id)
            db_session.add(role_permission)

        # Assign role to user
        user_role = (
            db_session.query(UserRole)
            .filter_by(user_id=regular_user.id, role_id=role.id)
            .first()
        )
        if not user_role:
            user_role = UserRole(user_id=regular_user.id, role_id=role.id)
            db_session.add(user_role)

        db_session.commit()

        with client.application.app_context():
            tokens = jwt_manager.generate_tokens(regular_user)
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    def test_update_security_settings_success(self, client, auth_headers_with_system_settings_permission, db_session):
        """Test successful update of security settings."""
        from models import AuditLog

        payload = {"session_timeout_minutes": 60}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=auth_headers_with_system_settings_permission
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data["session_timeout_minutes"] == 60
        assert data["source"] == "database"
        assert data["updated_by"] is not None
        assert data["updated_at"] is not None

        # Verify audit log was created
        audit_entry = db_session.query(AuditLog).filter_by(
            action_type="update_security_setting"
        ).first()
        assert audit_entry is not None
        assert "60 minutes" in audit_entry.action_details

    def test_update_security_settings_requires_permission(self, client, user_auth_headers):
        """Test that PUT endpoint requires system.settings permission."""
        payload = {"session_timeout_minutes": 60}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=user_auth_headers
        )

        # Should be forbidden without permission
        assert response.status_code == 403

    def test_update_security_settings_no_auth(self, client):
        """Test that PUT endpoint requires authentication."""
        payload = {"session_timeout_minutes": 60}
        response = client.put("/api/security/settings", json=payload)

        assert response.status_code == 401

    def test_update_security_settings_missing_field(self, client, auth_headers_with_system_settings_permission):
        """Test update with missing session_timeout_minutes field."""
        payload = {}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=auth_headers_with_system_settings_permission
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "session_timeout_minutes is required" in data["error"]

    def test_update_security_settings_null_value(self, client, auth_headers_with_system_settings_permission):
        """Test update with null session_timeout_minutes value."""
        payload = {"session_timeout_minutes": None}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=auth_headers_with_system_settings_permission
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "session_timeout_minutes is required" in data["error"]

    def test_update_security_settings_invalid_type_string(self, client, auth_headers_with_system_settings_permission):
        """Test update with non-numeric string value."""
        payload = {"session_timeout_minutes": "not_a_number"}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=auth_headers_with_system_settings_permission
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "must be an integer" in data["error"]

    def test_update_security_settings_invalid_type_list(self, client, auth_headers_with_system_settings_permission):
        """Test update with list value."""
        payload = {"session_timeout_minutes": [60]}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=auth_headers_with_system_settings_permission
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "must be an integer" in data["error"]

    def test_update_security_settings_value_below_minimum(self, client, auth_headers_with_system_settings_permission):
        """Test update with value below minimum (5 minutes)."""
        payload = {"session_timeout_minutes": 4}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=auth_headers_with_system_settings_permission
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "must be between 5 and 240 minutes" in data["error"]

    def test_update_security_settings_value_above_maximum(self, client, auth_headers_with_system_settings_permission):
        """Test update with value above maximum (240 minutes)."""
        payload = {"session_timeout_minutes": 241}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=auth_headers_with_system_settings_permission
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "must be between 5 and 240 minutes" in data["error"]

    def test_update_security_settings_minimum_boundary(self, client, auth_headers_with_system_settings_permission):
        """Test update with minimum valid value (5 minutes)."""
        payload = {"session_timeout_minutes": 5}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=auth_headers_with_system_settings_permission
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["session_timeout_minutes"] == 5

    def test_update_security_settings_maximum_boundary(self, client, auth_headers_with_system_settings_permission):
        """Test update with maximum valid value (240 minutes)."""
        payload = {"session_timeout_minutes": 240}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=auth_headers_with_system_settings_permission
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["session_timeout_minutes"] == 240

    def test_update_security_settings_string_integer(self, client, auth_headers_with_system_settings_permission):
        """Test update with string that can be converted to integer."""
        payload = {"session_timeout_minutes": "90"}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=auth_headers_with_system_settings_permission
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["session_timeout_minutes"] == 90

    def test_update_security_settings_empty_json_body(self, client, auth_headers_with_system_settings_permission):
        """Test update with completely empty request."""
        response = client.put(
            "/api/security/settings",
            data="",
            content_type="application/json",
            headers=auth_headers_with_system_settings_permission
        )

        # Empty JSON body causes parse error - may return 400 or 500 depending on error handler
        assert response.status_code in [400, 500]

    def test_update_security_settings_updates_existing(self, client, auth_headers_with_system_settings_permission, db_session):
        """Test that updating when setting already exists works correctly."""
        from models import SystemSetting
        from utils.system_settings import SESSION_TIMEOUT_KEY

        # First create an existing setting
        existing_setting = SystemSetting(
            key=SESSION_TIMEOUT_KEY,
            value="30",
            category="security",
            description="Session timeout",
            is_sensitive=False
        )
        db_session.add(existing_setting)
        db_session.commit()

        # Now update it
        payload = {"session_timeout_minutes": 120}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=auth_headers_with_system_settings_permission
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["session_timeout_minutes"] == 120

        # Verify only one setting exists
        settings_count = db_session.query(SystemSetting).filter_by(
            key=SESSION_TIMEOUT_KEY
        ).count()
        assert settings_count == 1

    def test_update_security_settings_audit_log_created(self, client, auth_headers_with_system_settings_permission, db_session):
        """Test that audit log entry is created on update."""
        from models import AuditLog

        initial_count = db_session.query(AuditLog).count()

        payload = {"session_timeout_minutes": 75}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=auth_headers_with_system_settings_permission
        )

        assert response.status_code == 200

        final_count = db_session.query(AuditLog).count()
        assert final_count == initial_count + 1

        # Verify audit log content
        audit_entry = db_session.query(AuditLog).filter(
            AuditLog.action_type == "update_security_setting"
        ).order_by(AuditLog.id.desc()).first()
        assert "75 minutes" in audit_entry.action_details

    def test_update_security_settings_response_format(self, client, auth_headers_with_system_settings_permission):
        """Test that response includes all expected fields with correct types."""
        payload = {"session_timeout_minutes": 100}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=auth_headers_with_system_settings_permission
        )

        assert response.status_code == 200
        data = response.get_json()

        # Check all fields exist
        assert "session_timeout_minutes" in data
        assert "default_timeout_minutes" in data
        assert "min_timeout_minutes" in data
        assert "max_timeout_minutes" in data
        assert "source" in data
        assert "updated_at" in data
        assert "updated_by" in data

        # Check types
        assert isinstance(data["session_timeout_minutes"], int)
        assert isinstance(data["default_timeout_minutes"], int)
        assert isinstance(data["min_timeout_minutes"], int)
        assert isinstance(data["max_timeout_minutes"], int)
        assert isinstance(data["source"], str)
        assert isinstance(data["updated_at"], str)  # ISO format string
        assert isinstance(data["updated_by"], dict)

    def test_update_security_settings_updated_by_structure(self, client, auth_headers_with_system_settings_permission):
        """Test that updated_by contains correct user information."""
        payload = {"session_timeout_minutes": 45}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=auth_headers_with_system_settings_permission
        )

        assert response.status_code == 200
        data = response.get_json()

        updated_by = data["updated_by"]
        assert "id" in updated_by
        assert "name" in updated_by
        assert "employee_number" in updated_by
        assert isinstance(updated_by["id"], int)
        assert isinstance(updated_by["name"], str)
        assert isinstance(updated_by["employee_number"], str)


class TestSecuritySettingsIntegration:
    """Integration tests for security settings endpoints."""

    @pytest.fixture
    def setup_permission(self, client, db_session, regular_user, jwt_manager):
        """Setup user with system.settings permission."""
        from models import Permission, Role, RolePermission, UserRole

        permission = db_session.query(Permission).filter_by(name="system.settings").first()
        if not permission:
            permission = Permission(
                name="system.settings",
                description="Manage system settings",
                category="System"
            )
            db_session.add(permission)
            db_session.flush()

        role = db_session.query(Role).filter_by(name="Settings Manager").first()
        if not role:
            role = Role(name="Settings Manager", description="Can manage system settings")
            db_session.add(role)
            db_session.flush()

        if not db_session.query(RolePermission).filter_by(role_id=role.id, permission_id=permission.id).first():
            db_session.add(RolePermission(role_id=role.id, permission_id=permission.id))

        if not db_session.query(UserRole).filter_by(user_id=regular_user.id, role_id=role.id).first():
            db_session.add(UserRole(user_id=regular_user.id, role_id=role.id))

        db_session.commit()

        with client.application.app_context():
            tokens = jwt_manager.generate_tokens(regular_user)
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    def test_get_after_update_reflects_changes(self, client, setup_permission, auth_headers):
        """Test that GET returns updated values after PUT."""
        # First update the setting
        payload = {"session_timeout_minutes": 180}
        update_response = client.put(
            "/api/security/settings",
            json=payload,
            headers=setup_permission
        )
        assert update_response.status_code == 200

        # Now fetch and verify
        get_response = client.get("/api/security/settings", headers=auth_headers)
        assert get_response.status_code == 200

        data = get_response.get_json()
        assert data["session_timeout_minutes"] == 180
        assert data["source"] == "database"

    def test_multiple_updates_track_correctly(self, client, setup_permission, db_session):
        """Test that multiple updates are tracked correctly."""
        from models import AuditLog

        # First update
        response1 = client.put(
            "/api/security/settings",
            json={"session_timeout_minutes": 30},
            headers=setup_permission
        )
        assert response1.status_code == 200

        # Second update
        response2 = client.put(
            "/api/security/settings",
            json={"session_timeout_minutes": 60},
            headers=setup_permission
        )
        assert response2.status_code == 200

        # Third update
        response3 = client.put(
            "/api/security/settings",
            json={"session_timeout_minutes": 90},
            headers=setup_permission
        )
        assert response3.status_code == 200

        data = response3.get_json()
        assert data["session_timeout_minutes"] == 90

        # Verify 3 audit entries
        audit_count = db_session.query(AuditLog).filter_by(
            action_type="update_security_setting"
        ).count()
        assert audit_count == 3

    def test_zero_timeout_is_invalid(self, client, setup_permission):
        """Test that zero timeout is invalid."""
        payload = {"session_timeout_minutes": 0}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=setup_permission
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "must be between" in data["error"]

    def test_negative_timeout_is_invalid(self, client, setup_permission):
        """Test that negative timeout is invalid."""
        payload = {"session_timeout_minutes": -10}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=setup_permission
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "must be between" in data["error"]

    def test_float_value_accepted_as_truncated_integer(self, client, setup_permission):
        """Test that float value is converted to integer."""
        payload = {"session_timeout_minutes": 60.5}
        response = client.put(
            "/api/security/settings",
            json=payload,
            headers=setup_permission
        )

        assert response.status_code == 200
        data = response.get_json()
        # Python int() truncates, so 60.5 becomes 60
        assert data["session_timeout_minutes"] == 60

    def test_update_refreshes_relationship_if_not_loaded(self, client, setup_permission, db_session, regular_user, monkeypatch):
        """Test that updated_by relationship is manually loaded when refresh clears it."""
        from unittest.mock import MagicMock, patch

        from models import SystemSetting
        from utils.system_settings import SESSION_TIMEOUT_KEY

        # Create an existing setting to ensure update path (not create)
        existing = SystemSetting(
            key=SESSION_TIMEOUT_KEY,
            value="30",
            category="security",
            description="Session timeout",
            is_sensitive=False,
            updated_by_id=regular_user.id
        )
        db_session.add(existing)
        db_session.commit()

        # Mock db.session.refresh to clear the relationship but keep the ID
        original_refresh = db_session.refresh

        def mock_refresh(obj):
            original_refresh(obj)
            # Simulate the case where refresh clears the relationship but keeps ID
            if hasattr(obj, 'updated_by'):
                object.__setattr__(obj, 'updated_by', None)

        with patch.object(db_session, 'refresh', side_effect=mock_refresh):
            payload = {"session_timeout_minutes": 100}
            response = client.put(
                "/api/security/settings",
                json=payload,
                headers=setup_permission
            )

        assert response.status_code == 200
        data = response.get_json()
        # Should still have updated_by info because of the manual reload logic
        assert data["updated_by"] is not None
        assert data["session_timeout_minutes"] == 100
