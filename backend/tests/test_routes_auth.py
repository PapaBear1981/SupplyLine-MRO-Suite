"""
Tests for JWT Authentication Routes

This module tests the authentication endpoints including:
- Login with JWT token generation
- Token refresh
- Logout (token invalidation)
- User profile retrieval
- Authentication status checks
- CSRF token generation
- Password change functionality
"""

import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from flask import g

from models import AuditLog, User, UserActivity


class TestLoginEndpoint:
    """Test the /api/auth/login endpoint"""

    def test_login_success(self, client, test_user, db_session):
        """Test successful login with valid credentials"""
        response = client.post("/api/auth/login", json={
            "employee_number": "USER001",
            "password": "user123"
        })

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["message"] == "Login successful"
        assert "user" in data
        assert data["user"]["employee_number"] == "USER001"
        assert data["user"]["name"] == "Test User"

        # Check that HttpOnly cookies are set
        cookies = response.headers.getlist("Set-Cookie")
        assert any("access_token=" in cookie for cookie in cookies)
        assert any("refresh_token=" in cookie for cookie in cookies)
        assert any("HttpOnly" in cookie for cookie in cookies)

    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post("/api/auth/login", json={})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Missing employee_number or password" in data["error"]

    def test_login_missing_password(self, client):
        """Test login with missing password"""
        response = client.post("/api/auth/login", json={
            "employee_number": "USER001"
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Missing employee_number or password" in data["error"]

    def test_login_missing_employee_number(self, client):
        """Test login with missing employee number"""
        response = client.post("/api/auth/login", json={
            "password": "user123"
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Missing employee_number or password" in data["error"]

    def test_login_invalid_user(self, client, db_session):
        """Test login with non-existent user"""
        response = client.post("/api/auth/login", json={
            "employee_number": "NONEXISTENT",
            "password": "password123"
        })

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data["code"] == "INVALID_CREDENTIALS"
        # Generic error message should not reveal if user exists
        assert "Invalid employee number or password" in data["error"]

    def test_login_wrong_password(self, client, test_user, db_session):
        """Test login with incorrect password"""
        response = client.post("/api/auth/login", json={
            "employee_number": "USER001",
            "password": "wrongpassword"
        })

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data["code"] == "INVALID_CREDENTIALS"

        # Verify failed login attempt was recorded
        db_session.refresh(test_user)
        assert test_user.failed_login_attempts > 0

    def test_login_inactive_user(self, client, db_session):
        """Test login with inactive user account"""
        inactive_user = User(
            name="Inactive User",
            employee_number="INACTIVE001",
            department="Engineering",
            is_admin=False,
            is_active=False
        )
        inactive_user.set_password("password123")
        db_session.add(inactive_user)
        db_session.commit()

        response = client.post("/api/auth/login", json={
            "employee_number": "INACTIVE001",
            "password": "password123"
        })

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data["code"] == "INVALID_CREDENTIALS"

    def test_login_locked_account(self, client, db_session):
        """Test login with locked account"""
        locked_user = User(
            name="Locked User",
            employee_number="LOCKED001",
            department="Engineering",
            is_admin=False,
            is_active=True
        )
        locked_user.set_password("password123")
        # Simulate account lockout
        locked_user.failed_login_attempts = 5
        locked_user.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
        db_session.add(locked_user)
        db_session.commit()

        response = client.post("/api/auth/login", json={
            "employee_number": "LOCKED001",
            "password": "password123"
        })

        assert response.status_code == 423
        data = json.loads(response.data)
        assert data["code"] == "ACCOUNT_LOCKED"

    def test_login_force_password_change(self, client, db_session):
        """Test login when user must change password"""
        user = User(
            name="Force Change User",
            employee_number="FORCE001",
            department="Engineering",
            is_admin=False,
            is_active=True,
            force_password_change=True
        )
        user.set_password("temppass123")
        db_session.add(user)
        db_session.commit()

        response = client.post("/api/auth/login", json={
            "employee_number": "FORCE001",
            "password": "temppass123"
        })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == "PASSWORD_CHANGE_REQUIRED"
        assert data["user_id"] == user.id

    def test_login_invalid_json(self, client):
        """Test login with invalid JSON payload"""
        response = client.post("/api/auth/login",
                               data="invalid json",
                               content_type="application/json")

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["code"] == "INVALID_JSON"

    def test_login_logs_activity(self, client, test_user, db_session):
        """Test that successful login creates activity and audit logs"""
        response = client.post("/api/auth/login", json={
            "employee_number": "USER001",
            "password": "user123"
        })

        assert response.status_code == 200

        # Check user activity log
        activity = UserActivity.query.filter_by(
            user_id=test_user.id,
            activity_type="login"
        ).first()
        assert activity is not None
        assert "JWT" in activity.description

        # Check audit log
        audit = AuditLog.query.filter_by(
            action_type="user_login"
        ).order_by(AuditLog.id.desc()).first()
        assert audit is not None
        assert str(test_user.id) in audit.action_details


class TestLogoutEndpoint:
    """Test the /api/auth/logout endpoint"""

    def test_logout_success(self, client, auth_headers_user):
        """Test successful logout"""
        response = client.post("/api/auth/logout", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Logged out successfully"

        # Check that cookies are cleared
        cookies = response.headers.getlist("Set-Cookie")
        access_cookie = [c for c in cookies if "access_token=" in c]
        refresh_cookie = [c for c in cookies if "refresh_token=" in c]
        assert len(access_cookie) > 0
        assert len(refresh_cookie) > 0
        # Cookies should be cleared with empty value
        assert any("access_token=;" in c or "max-age=0" in c.lower() for c in access_cookie)

    def test_logout_without_auth(self, client):
        """Test logout without authentication"""
        response = client.post("/api/auth/logout")

        assert response.status_code == 401

    def test_logout_logs_activity(self, client, auth_headers_user, test_user, db_session):
        """Test that logout creates activity log"""
        response = client.post("/api/auth/logout", headers=auth_headers_user)

        assert response.status_code == 200

        # Check user activity log
        activity = UserActivity.query.filter_by(
            user_id=test_user.id,
            activity_type="logout"
        ).first()
        assert activity is not None


class TestRefreshTokenEndpoint:
    """Test the /api/auth/refresh endpoint"""

    def test_refresh_token_from_cookie(self, client, test_user, jwt_manager):
        """Test token refresh using HttpOnly cookie"""
        # First login to get tokens
        login_response = client.post("/api/auth/login", json={
            "employee_number": "USER001",
            "password": "user123"
        })
        assert login_response.status_code == 200

        # The refresh token should be in cookies
        # Make refresh request - cookies are automatically sent
        response = client.post("/api/auth/refresh")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Tokens refreshed successfully"

        # Check that new cookies are set
        cookies = response.headers.getlist("Set-Cookie")
        assert any("access_token=" in cookie for cookie in cookies)
        assert any("refresh_token=" in cookie for cookie in cookies)

    def test_refresh_token_from_body(self, client, test_user, jwt_manager):
        """Test token refresh using request body (legacy support)"""
        # Generate tokens directly
        tokens = jwt_manager.generate_tokens(test_user)

        response = client.post("/api/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Tokens refreshed successfully"

    def test_refresh_token_missing(self, client):
        """Test refresh without token"""
        response = client.post("/api/auth/refresh", json={})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["code"] == "MISSING_REFRESH_TOKEN"

    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token"""
        response = client.post("/api/auth/refresh", json={
            "refresh_token": "invalid-token"
        })

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data["code"] == "INVALID_REFRESH_TOKEN"


class TestGetCurrentUserEndpoint:
    """Test the /api/auth/me endpoint"""

    def test_get_current_user_success(self, client, auth_headers_user, test_user):
        """Test getting current user info"""
        response = client.get("/api/auth/me", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "user" in data
        assert data["user"]["id"] == test_user.id
        assert data["user"]["employee_number"] == "USER001"
        assert data["user"]["name"] == "Test User"

    def test_get_current_user_admin(self, client, auth_headers_admin, admin_user):
        """Test getting current admin user info"""
        response = client.get("/api/auth/me", headers=auth_headers_admin)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["user"]["is_admin"] is True

    def test_get_current_user_without_auth(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/auth/me")

        assert response.status_code == 401

    def test_get_current_user_inactive(self, client, db_session, jwt_manager):
        """Test getting current user when user becomes inactive"""
        user = User(
            name="Deactivated User",
            employee_number="DEACT001",
            department="Engineering",
            is_admin=False,
            is_active=True
        )
        user.set_password("password123")
        db_session.add(user)
        db_session.commit()

        # Generate token while user is active
        tokens = jwt_manager.generate_tokens(user)
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Deactivate user
        user.is_active = False
        db_session.commit()

        # Try to get user info
        response = client.get("/api/auth/me", headers=headers)

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["code"] == "USER_NOT_FOUND"


class TestAuthStatusEndpoint:
    """Test the /api/auth/status endpoint"""

    def test_auth_status_authenticated(self, client, test_user, jwt_manager):
        """Test auth status when authenticated"""
        # Login first to set cookies
        client.post("/api/auth/login", json={
            "employee_number": "USER001",
            "password": "user123"
        })

        response = client.get("/api/auth/status")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["authenticated"] is True
        assert "user" in data
        assert data["user"]["employee_number"] == "USER001"

    def test_auth_status_not_authenticated(self, client):
        """Test auth status when not authenticated"""
        response = client.get("/api/auth/status")

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["authenticated"] is False
        assert data["message"] == "Not authenticated"


class TestCSRFTokenEndpoint:
    """Test the /api/auth/csrf-token endpoint"""

    def test_get_csrf_token_success(self, client, auth_headers_user):
        """Test getting CSRF token"""
        response = client.get("/api/auth/csrf-token", headers=auth_headers_user)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "csrf_token" in data
        assert isinstance(data["csrf_token"], str)
        assert len(data["csrf_token"]) > 0
        assert data["expires_in"] == 3600

    def test_get_csrf_token_without_auth(self, client):
        """Test getting CSRF token without authentication"""
        response = client.get("/api/auth/csrf-token")

        assert response.status_code == 401


class TestChangePasswordEndpoint:
    """Test the /api/auth/change-password endpoint"""

    def test_change_password_success(self, client, db_session):
        """Test successful password change"""
        user = User(
            name="Change Password User",
            employee_number="CHANGE001",
            department="Engineering",
            is_admin=False,
            is_active=True,
            force_password_change=True
        )
        user.set_password("OldPass123!")
        db_session.add(user)
        db_session.commit()

        response = client.post("/api/auth/change-password", json={
            "employee_number": "CHANGE001",
            "current_password": "OldPass123!",
            "new_password": "NewPass456@"
        })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Password changed successfully"
        assert "user" in data

        # Verify force_password_change flag is cleared
        db_session.refresh(user)
        assert user.force_password_change is False

        # Verify password was changed
        assert user.check_password("NewPass456@")

        # Check that cookies are set
        cookies = response.headers.getlist("Set-Cookie")
        assert any("access_token=" in cookie for cookie in cookies)

    def test_change_password_missing_fields(self, client):
        """Test password change with missing fields"""
        response = client.post("/api/auth/change-password", json={
            "employee_number": "CHANGE001"
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Missing required fields" in data["error"]

    def test_change_password_invalid_user(self, client):
        """Test password change for non-existent user"""
        response = client.post("/api/auth/change-password", json={
            "employee_number": "NONEXISTENT",
            "current_password": "OldPass123!",
            "new_password": "NewPass456@"
        })

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "Invalid credentials" in data["error"]

    def test_change_password_wrong_current(self, client, db_session):
        """Test password change with wrong current password"""
        user = User(
            name="Wrong Current Pass",
            employee_number="WRONG001",
            department="Engineering",
            is_admin=False,
            is_active=True,
            force_password_change=True
        )
        user.set_password("CorrectPass123!")
        db_session.add(user)
        db_session.commit()

        response = client.post("/api/auth/change-password", json={
            "employee_number": "WRONG001",
            "current_password": "WrongPass123!",
            "new_password": "NewPass456@"
        })

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "Invalid current password" in data["error"]

    def test_change_password_not_required(self, client, db_session):
        """Test password change when not required"""
        user = User(
            name="No Change Required",
            employee_number="NOCHANGE001",
            department="Engineering",
            is_admin=False,
            is_active=True,
            force_password_change=False
        )
        user.set_password("OldPass123!")
        db_session.add(user)
        db_session.commit()

        response = client.post("/api/auth/change-password", json={
            "employee_number": "NOCHANGE001",
            "current_password": "OldPass123!",
            "new_password": "NewPass456@"
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Password change not required" in data["error"]

    def test_change_password_weak_password(self, client, db_session):
        """Test password change with weak password"""
        user = User(
            name="Weak Password User",
            employee_number="WEAK001",
            department="Engineering",
            is_admin=False,
            is_active=True,
            force_password_change=True
        )
        user.set_password("OldPass123!")
        db_session.add(user)
        db_session.commit()

        response = client.post("/api/auth/change-password", json={
            "employee_number": "WEAK001",
            "current_password": "OldPass123!",
            "new_password": "weak"
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "does not meet security requirements" in data["error"]

    def test_change_password_logs_activity(self, client, db_session):
        """Test that password change creates activity log"""
        user = User(
            name="Log Activity User",
            employee_number="LOG001",
            department="Engineering",
            is_admin=False,
            is_active=True,
            force_password_change=True
        )
        user.set_password("OldPass123!")
        db_session.add(user)
        db_session.commit()

        response = client.post("/api/auth/change-password", json={
            "employee_number": "LOG001",
            "current_password": "OldPass123!",
            "new_password": "NewPass456@"
        })

        assert response.status_code == 200

        # Check user activity log
        activity = UserActivity.query.filter_by(
            user_id=user.id,
            activity_type="password_change"
        ).first()
        assert activity is not None


class TestSecurityFeatures:
    """Test security features of authentication"""

    def test_timing_safe_auth_nonexistent_user(self, client, db_session):
        """Test that auth is timing-safe for non-existent users"""
        # This test verifies that the same error is returned whether
        # the user exists or not, preventing user enumeration
        response = client.post("/api/auth/login", json={
            "employee_number": "NONEXISTENT",
            "password": "wrongpassword"
        })

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data["code"] == "INVALID_CREDENTIALS"
        assert "Invalid employee number or password" in data["error"]

    def test_failed_login_increments_counter(self, client, test_user, db_session):
        """Test that failed logins increment the counter"""
        initial_attempts = test_user.failed_login_attempts

        client.post("/api/auth/login", json={
            "employee_number": "USER001",
            "password": "wrongpassword"
        })

        db_session.refresh(test_user)
        assert test_user.failed_login_attempts == initial_attempts + 1

    def test_successful_login_resets_counter(self, client, test_user, db_session):
        """Test that successful login resets failed attempt counter"""
        # Set some failed attempts
        test_user.failed_login_attempts = 3
        db_session.commit()

        client.post("/api/auth/login", json={
            "employee_number": "USER001",
            "password": "user123"
        })

        db_session.refresh(test_user)
        assert test_user.failed_login_attempts == 0

    def test_cookies_have_security_flags(self, client, test_user):
        """Test that cookies have proper security flags"""
        response = client.post("/api/auth/login", json={
            "employee_number": "USER001",
            "password": "user123"
        })

        cookies = response.headers.getlist("Set-Cookie")

        for cookie in cookies:
            if "access_token=" in cookie or "refresh_token=" in cookie:
                # Check HttpOnly flag
                assert "HttpOnly" in cookie
                # Check SameSite flag
                assert "SameSite" in cookie


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_login_empty_json(self, client):
        """Test login with empty JSON object"""
        response = client.post("/api/auth/login", json={})

        assert response.status_code == 400

    def test_login_with_extra_fields(self, client, test_user):
        """Test login ignores extra fields"""
        response = client.post("/api/auth/login", json={
            "employee_number": "USER001",
            "password": "user123",
            "extra_field": "should be ignored",
            "another_field": 12345
        })

        assert response.status_code == 200

    def test_concurrent_logins_allowed(self, client, test_user):
        """Test that multiple concurrent logins are allowed"""
        # First login
        response1 = client.post("/api/auth/login", json={
            "employee_number": "USER001",
            "password": "user123"
        })
        assert response1.status_code == 200

        # Second login should also succeed
        response2 = client.post("/api/auth/login", json={
            "employee_number": "USER001",
            "password": "user123"
        })
        assert response2.status_code == 200
