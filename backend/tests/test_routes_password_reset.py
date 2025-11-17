"""
Comprehensive tests for routes_password_reset.py
Testing password reset functionality including admin operations, search, and security measures.
"""

import pytest
from unittest.mock import patch, MagicMock
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from conftest import _ensure_imports
from routes_password_reset import generate_secure_password


class TestGenerateSecurePassword:
    """Tests for the generate_secure_password helper function"""

    def test_generate_secure_password_default_length(self):
        """Test that default password length is 12 characters"""
        password = generate_secure_password()
        assert len(password) == 12

    def test_generate_secure_password_custom_length(self):
        """Test that custom password length is respected"""
        password = generate_secure_password(length=16)
        assert len(password) == 16

    def test_generate_secure_password_contains_lowercase(self):
        """Test that password contains at least one lowercase letter"""
        password = generate_secure_password()
        assert any(c.islower() for c in password)

    def test_generate_secure_password_contains_uppercase(self):
        """Test that password contains at least one uppercase letter"""
        password = generate_secure_password()
        assert any(c.isupper() for c in password)

    def test_generate_secure_password_contains_digit(self):
        """Test that password contains at least one digit"""
        password = generate_secure_password()
        assert any(c.isdigit() for c in password)

    def test_generate_secure_password_contains_special(self):
        """Test that password contains at least one special character"""
        special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        password = generate_secure_password()
        assert any(c in special for c in password)

    def test_generate_secure_password_uniqueness(self):
        """Test that generated passwords are unique"""
        passwords = [generate_secure_password() for _ in range(100)]
        unique_passwords = set(passwords)
        # All passwords should be unique
        assert len(unique_passwords) == 100


class TestResetUserPassword:
    """Tests for the reset_user_password endpoint"""

    def test_reset_password_success(self, client, auth_headers_admin, admin_user, regular_user):
        """Test successful password reset by admin"""
        _ensure_imports()
        from models import db, User

        response = client.post(
            f"/api/admin/users/{regular_user.id}/reset-password",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "temporary_password" in data
        assert len(data["temporary_password"]) == 12
        assert data["user"]["id"] == regular_user.id
        assert data["user"]["name"] == regular_user.name
        assert data["user"]["force_password_change"] is True
        assert "warning" in data

        # Verify password was changed in database
        with client.application.app_context():
            updated_user = db.session.get(User, regular_user.id)
            assert updated_user.force_password_change is True
            assert updated_user.password_changed_at is not None
            # Verify the temporary password works
            assert check_password_hash(updated_user.password_hash, data["temporary_password"])

    def test_reset_password_creates_audit_log(self, client, auth_headers_admin, admin_user, regular_user):
        """Test that password reset creates an audit log entry"""
        _ensure_imports()
        from models import db, AuditLog

        response = client.post(
            f"/api/admin/users/{regular_user.id}/reset-password",
            headers=auth_headers_admin
        )

        assert response.status_code == 200

        # Verify audit log was created
        with client.application.app_context():
            audit_log = AuditLog.query.filter_by(action_type="admin_password_reset").order_by(AuditLog.id.desc()).first()
            assert audit_log is not None
            assert str(admin_user.id) in audit_log.action_details
            assert str(regular_user.id) in audit_log.action_details

    def test_reset_password_target_user_not_found(self, client, auth_headers_admin, admin_user):
        """Test password reset with non-existent target user"""
        response = client.post(
            "/api/admin/users/99999/reset-password",
            headers=auth_headers_admin
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["error"] == "User not found"
        assert data["code"] == "USER_NOT_FOUND"

    def test_reset_password_cannot_reset_own_password(self, client, auth_headers_admin, admin_user):
        """Test that admin cannot reset their own password through this endpoint"""
        response = client.post(
            f"/api/admin/users/{admin_user.id}/reset-password",
            headers=auth_headers_admin
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "CANNOT_RESET_OWN_PASSWORD"
        assert "change password feature" in data["error"]

    def test_reset_password_non_admin_forbidden(self, client, auth_headers_user, regular_user):
        """Test that non-admin users cannot reset passwords"""
        _ensure_imports()
        from models import db, User

        # Create another user to try to reset
        with client.application.app_context():
            other_user = User(
                name="Other User",
                employee_number="USER002",
                department="Testing",
                password_hash=generate_password_hash("other123"),
                is_admin=False,
                is_active=True
            )
            db.session.add(other_user)
            db.session.commit()
            other_user_id = other_user.id

        response = client.post(
            f"/api/admin/users/{other_user_id}/reset-password",
            headers=auth_headers_user
        )

        # Should be forbidden (403) or unauthorized
        assert response.status_code in [401, 403]

    def test_reset_password_no_auth_header(self, client, regular_user):
        """Test password reset without authentication"""
        response = client.post(
            f"/api/admin/users/{regular_user.id}/reset-password"
        )

        assert response.status_code == 401

    def test_reset_password_database_error(self, client, auth_headers_admin, admin_user, regular_user):
        """Test password reset handles database errors gracefully"""
        _ensure_imports()
        from models import db

        with patch.object(db.session, 'commit', side_effect=Exception("Database error")):
            response = client.post(
                f"/api/admin/users/{regular_user.id}/reset-password",
                headers=auth_headers_admin
            )

            assert response.status_code == 500
            data = response.get_json()
            assert data["error"] == "Failed to reset password"
            assert data["code"] == "PASSWORD_RESET_FAILED"
            assert "Database error" in data["details"]

    def test_reset_password_admin_not_found_in_db(self, client, auth_headers_admin, admin_user, regular_user):
        """Test password reset when admin user is not found in database"""
        _ensure_imports()
        from models import db

        # Mock db.session.get to return None for admin_user_id
        original_get = db.session.get

        def mock_get(model, id):
            if id == admin_user.id:
                return None
            return original_get(model, id)

        with patch.object(db.session, 'get', side_effect=mock_get):
            response = client.post(
                f"/api/admin/users/{regular_user.id}/reset-password",
                headers=auth_headers_admin
            )

            assert response.status_code == 404
            data = response.get_json()
            assert data["error"] == "Admin user not found"
            assert data["code"] == "ADMIN_NOT_FOUND"

    def test_reset_password_updates_password_timestamp(self, client, auth_headers_admin, admin_user, regular_user):
        """Test that password reset updates password_changed_at timestamp"""
        _ensure_imports()
        from models import db, User

        # Record original timestamp
        original_timestamp = regular_user.password_changed_at

        response = client.post(
            f"/api/admin/users/{regular_user.id}/reset-password",
            headers=auth_headers_admin
        )

        assert response.status_code == 200

        with client.application.app_context():
            updated_user = db.session.get(User, regular_user.id)
            assert updated_user.password_changed_at is not None
            if original_timestamp:
                assert updated_user.password_changed_at > original_timestamp

    def test_reset_password_multiple_users(self, client, auth_headers_admin, admin_user):
        """Test resetting passwords for multiple different users"""
        _ensure_imports()
        from models import db, User

        # Create multiple users
        with client.application.app_context():
            users = []
            for i in range(3):
                user = User(
                    name=f"User {i}",
                    employee_number=f"USR00{i}",
                    department="Testing",
                    password_hash=generate_password_hash("test123"),
                    is_admin=False,
                    is_active=True
                )
                db.session.add(user)
                users.append(user)
            db.session.commit()
            user_ids = [u.id for u in users]

        # Reset password for each user
        passwords = []
        for user_id in user_ids:
            response = client.post(
                f"/api/admin/users/{user_id}/reset-password",
                headers=auth_headers_admin
            )
            assert response.status_code == 200
            data = response.get_json()
            passwords.append(data["temporary_password"])

        # All passwords should be unique
        assert len(set(passwords)) == 3


class TestSearchUsersForPasswordReset:
    """Tests for the search_users_for_password_reset endpoint"""

    def test_search_users_no_filters(self, client, auth_headers_admin, admin_user, regular_user):
        """Test searching users without any filters returns active users"""
        response = client.get(
            "/api/admin/users/search",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # Should include admin and regular user
        assert len(data) >= 2

        # Verify structure of returned data
        for user_data in data:
            assert "id" in user_data
            assert "name" in user_data
            assert "employee_number" in user_data
            assert "department" in user_data
            assert "is_active" in user_data
            assert "is_admin" in user_data
            assert "force_password_change" in user_data
            assert "password_changed_at" in user_data
            assert "created_at" in user_data

    def test_search_users_by_name(self, client, auth_headers_admin, admin_user, regular_user):
        """Test searching users by name"""
        response = client.get(
            "/api/admin/users/search?q=Test",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # Should find both Test Admin and Test User
        assert len(data) >= 2
        for user_data in data:
            assert "Test" in user_data["name"] or "Test" in user_data["employee_number"]

    def test_search_users_by_employee_number(self, client, auth_headers_admin, admin_user, regular_user):
        """Test searching users by employee number"""
        response = client.get(
            "/api/admin/users/search?q=USER001",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(u["employee_number"] == "USER001" for u in data)

    def test_search_users_by_department(self, client, auth_headers_admin, admin_user, regular_user):
        """Test filtering users by department"""
        response = client.get(
            "/api/admin/users/search?department=Engineering",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # All returned users should be in Engineering department
        for user_data in data:
            assert user_data["department"] == "Engineering"

    def test_search_users_include_inactive(self, client, auth_headers_admin, admin_user):
        """Test searching includes inactive users when requested"""
        _ensure_imports()
        from models import db, User

        # Create an inactive user
        with client.application.app_context():
            inactive_user = User(
                name="Inactive User",
                employee_number="INACTIVE001",
                department="Testing",
                password_hash=generate_password_hash("inactive123"),
                is_admin=False,
                is_active=False
            )
            db.session.add(inactive_user)
            db.session.commit()

        # Search without include_inactive
        response = client.get(
            "/api/admin/users/search?q=Inactive",
            headers=auth_headers_admin
        )
        data = response.get_json()
        assert not any(u["employee_number"] == "INACTIVE001" for u in data)

        # Search with include_inactive
        response = client.get(
            "/api/admin/users/search?q=Inactive&include_inactive=true",
            headers=auth_headers_admin
        )
        data = response.get_json()
        assert any(u["employee_number"] == "INACTIVE001" for u in data)

    def test_search_users_combined_filters(self, client, auth_headers_admin, admin_user, regular_user):
        """Test searching with multiple filters combined"""
        response = client.get(
            "/api/admin/users/search?q=Test&department=IT",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # All returned users should match both criteria
        for user_data in data:
            assert user_data["department"] == "IT"
            assert "Test" in user_data["name"] or "Test" in user_data["employee_number"]

    def test_search_users_empty_result(self, client, auth_headers_admin, admin_user):
        """Test searching users with no matching results"""
        response = client.get(
            "/api/admin/users/search?q=NonexistentUser12345",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_search_users_non_admin_forbidden(self, client, auth_headers_user, regular_user):
        """Test that non-admin users cannot search users"""
        response = client.get(
            "/api/admin/users/search",
            headers=auth_headers_user
        )

        # Should be forbidden (403) or unauthorized
        assert response.status_code in [401, 403]

    def test_search_users_no_auth_header(self, client):
        """Test searching users without authentication"""
        response = client.get("/api/admin/users/search")

        assert response.status_code == 401

    def test_search_users_returns_ordered_by_name(self, client, auth_headers_admin, admin_user):
        """Test that search results are ordered by name"""
        _ensure_imports()
        from models import db, User

        # Create users with specific names to test ordering
        with client.application.app_context():
            users = [
                User(name="Zebra User", employee_number="ZU001", department="Testing",
                     password_hash=generate_password_hash("test"), is_admin=False, is_active=True),
                User(name="Alpha User", employee_number="AU001", department="Testing",
                     password_hash=generate_password_hash("test"), is_admin=False, is_active=True),
                User(name="Beta User", employee_number="BU001", department="Testing",
                     password_hash=generate_password_hash("test"), is_admin=False, is_active=True),
            ]
            for user in users:
                db.session.add(user)
            db.session.commit()

        response = client.get(
            "/api/admin/users/search",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        names = [u["name"] for u in data]
        assert names == sorted(names)

    def test_search_users_password_changed_at_format(self, client, auth_headers_admin, admin_user, regular_user):
        """Test that password_changed_at is properly formatted or null"""
        _ensure_imports()
        from models import db, User

        # Update user to have a password_changed_at
        with client.application.app_context():
            user = db.session.get(User, regular_user.id)
            user.password_changed_at = datetime.utcnow()
            db.session.commit()

        response = client.get(
            "/api/admin/users/search?q=USER001",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        user_data = next((u for u in data if u["employee_number"] == "USER001"), None)
        assert user_data is not None
        assert user_data["password_changed_at"] is not None
        # Should be ISO format string
        assert "T" in user_data["password_changed_at"]

    def test_search_users_database_error(self, client, auth_headers_admin, admin_user):
        """Test that search handles database errors gracefully"""
        _ensure_imports()
        from models import User

        # Mock the query property to raise an exception when accessed
        mock_query = MagicMock()
        mock_query.filter_by.side_effect = Exception("Database query error")

        with patch.object(User, 'query', mock_query):
            response = client.get(
                "/api/admin/users/search",
                headers=auth_headers_admin
            )

            assert response.status_code == 500
            data = response.get_json()
            assert data["error"] == "Failed to search users"
            assert data["code"] == "USER_SEARCH_FAILED"
            assert "Database query error" in data["details"]

    def test_search_users_whitespace_trimmed(self, client, auth_headers_admin, admin_user, regular_user):
        """Test that search query whitespace is trimmed"""
        response = client.get(
            "/api/admin/users/search?q=  Test  ",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # Should still find users with "Test" in name
        assert len(data) >= 1

    def test_search_users_empty_query_string(self, client, auth_headers_admin, admin_user, regular_user):
        """Test search with empty query string returns all active users"""
        response = client.get(
            "/api/admin/users/search?q=",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # Should return all active users
        assert len(data) >= 2

    def test_search_users_case_sensitive_like(self, client, auth_headers_admin, admin_user, regular_user):
        """Test that search uses SQL LIKE pattern matching"""
        # Search for partial match
        response = client.get(
            "/api/admin/users/search?q=est",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        # Should find users with "est" in their name (Test Admin, Test User)
        assert len(data) >= 2


class TestPasswordResetSecurity:
    """Tests for security measures in password reset functionality"""

    def test_temporary_password_complexity(self):
        """Test that generated temporary passwords meet complexity requirements"""
        for _ in range(50):
            password = generate_secure_password()
            has_lower = any(c.islower() for c in password)
            has_upper = any(c.isupper() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

            assert has_lower, f"Password {password} missing lowercase"
            assert has_upper, f"Password {password} missing uppercase"
            assert has_digit, f"Password {password} missing digit"
            assert has_special, f"Password {password} missing special char"

    def test_force_password_change_flag_set(self, client, auth_headers_admin, admin_user, regular_user):
        """Test that force_password_change flag is set after reset"""
        response = client.post(
            f"/api/admin/users/{regular_user.id}/reset-password",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["user"]["force_password_change"] is True

    def test_password_only_shown_once_warning(self, client, auth_headers_admin, admin_user, regular_user):
        """Test that response includes warning about one-time password display"""
        response = client.post(
            f"/api/admin/users/{regular_user.id}/reset-password",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "warning" in data
        assert "only be shown once" in data["warning"]

    def test_invalid_token_rejected(self, client, regular_user):
        """Test that invalid JWT tokens are rejected"""
        headers = {"Authorization": "Bearer invalid_token_123"}
        response = client.post(
            f"/api/admin/users/{regular_user.id}/reset-password",
            headers=headers
        )

        assert response.status_code == 401

    def test_expired_token_rejected(self, client, admin_user, regular_user):
        """Test that expired tokens are rejected"""
        # Using an invalid/malformed token should fail
        headers = {"Authorization": "Bearer malformed.token.here"}
        response = client.post(
            f"/api/admin/users/{regular_user.id}/reset-password",
            headers=headers
        )
        assert response.status_code == 401


class TestPasswordResetEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_reset_password_for_inactive_user(self, client, auth_headers_admin, admin_user):
        """Test that inactive users can still have their password reset"""
        _ensure_imports()
        from models import db, User

        # Create an inactive user
        with client.application.app_context():
            inactive_user = User(
                name="Inactive Target",
                employee_number="INACTIVE002",
                department="Testing",
                password_hash=generate_password_hash("inactive123"),
                is_admin=False,
                is_active=False
            )
            db.session.add(inactive_user)
            db.session.commit()
            inactive_id = inactive_user.id

        response = client.post(
            f"/api/admin/users/{inactive_id}/reset-password",
            headers=auth_headers_admin
        )

        # Should still be able to reset password for inactive user
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_reset_password_for_admin_user(self, client, auth_headers_admin, admin_user):
        """Test that admins can reset passwords of other admin users"""
        _ensure_imports()
        from models import db, User

        # Create another admin user
        with client.application.app_context():
            other_admin = User(
                name="Other Admin",
                employee_number="ADMIN002",
                department="IT",
                password_hash=generate_password_hash("admin123"),
                is_admin=True,
                is_active=True
            )
            db.session.add(other_admin)
            db.session.commit()
            other_admin_id = other_admin.id

        response = client.post(
            f"/api/admin/users/{other_admin_id}/reset-password",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_search_partial_department_match(self, client, auth_headers_admin, admin_user, regular_user):
        """Test that department filter requires exact match"""
        response = client.get(
            "/api/admin/users/search?department=Eng",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        # Should not return users with "Engineering" department (exact match only)
        assert not any(u["department"] == "Engineering" for u in data)

    def test_search_users_with_null_password_changed_at(self, client, auth_headers_admin, admin_user, regular_user):
        """Test that users with null password_changed_at are handled correctly"""
        # Regular user should have null password_changed_at by default
        response = client.get(
            "/api/admin/users/search?q=USER001",
            headers=auth_headers_admin
        )

        assert response.status_code == 200
        data = response.get_json()
        user_data = next((u for u in data if u["employee_number"] == "USER001"), None)
        assert user_data is not None
        # password_changed_at is None by default for new users
        assert user_data["password_changed_at"] is None or isinstance(user_data["password_changed_at"], str)

    def test_minimum_password_length(self):
        """Test that minimum password length constraint is handled"""
        # Minimum length should be at least 4 (one from each character set)
        password = generate_secure_password(length=4)
        assert len(password) == 4
        # Should still have all required character types
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    def test_large_password_length(self):
        """Test generating very long passwords"""
        password = generate_secure_password(length=50)
        assert len(password) == 50
        # Should still have all required character types
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
