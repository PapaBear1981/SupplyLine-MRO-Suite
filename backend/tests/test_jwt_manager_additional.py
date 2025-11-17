"""
Comprehensive test coverage for JWT Manager module
Tests token generation, validation, refresh, revocation, decorators, and error handling
"""

import time
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import jwt
import pytest
from flask import Flask, jsonify

from auth import JWTManager
from auth.jwt_manager import (
    admin_required,
    csrf_required,
    department_required,
    jwt_required,
    permission_required,
    permission_required_any,
)
from models import User, db


class TestJWTTokenGeneration:
    """Test token generation functionality"""

    def test_generate_tokens_structure(self, app, admin_user):
        """Test that generated tokens have correct structure"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)

            assert isinstance(tokens, dict)
            assert "access_token" in tokens
            assert "refresh_token" in tokens
            assert "expires_in" in tokens
            assert "token_type" in tokens
            assert tokens["expires_in"] == 900  # 15 minutes
            assert tokens["token_type"] == "Bearer"

    def test_access_token_payload_contents(self, app, admin_user):
        """Test that access token contains all required fields"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            secret_key = app.config["JWT_SECRET_KEY"]
            payload = jwt.decode(tokens["access_token"], secret_key, algorithms=["HS256"])

            assert payload["user_id"] == admin_user.id
            assert payload["user_name"] == admin_user.name
            assert payload["employee_number"] == admin_user.employee_number
            assert payload["is_admin"] == admin_user.is_admin
            assert payload["department"] == admin_user.department
            assert "permissions" in payload
            assert payload["type"] == "access"
            assert "jti" in payload  # JWT ID
            assert len(payload["jti"]) == 32  # hex(16) = 32 chars

    def test_refresh_token_payload_contents(self, app, admin_user):
        """Test that refresh token contains correct fields"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            secret_key = app.config["JWT_SECRET_KEY"]
            payload = jwt.decode(tokens["refresh_token"], secret_key, algorithms=["HS256"])

            assert payload["user_id"] == admin_user.id
            assert payload["type"] == "refresh"
            assert "jti" in payload
            # Refresh token should NOT contain sensitive user info
            assert "is_admin" not in payload
            assert "permissions" not in payload

    def test_token_expiration_times(self, app, admin_user):
        """Test that tokens have correct expiration times"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            secret_key = app.config["JWT_SECRET_KEY"]

            access_payload = jwt.decode(tokens["access_token"], secret_key, algorithms=["HS256"])
            refresh_payload = jwt.decode(tokens["refresh_token"], secret_key, algorithms=["HS256"])

            # Access token expires in ~15 minutes
            access_exp_diff = access_payload["exp"] - access_payload["iat"]
            assert access_exp_diff == 900  # 15 * 60 seconds

            # Refresh token expires in ~7 days
            refresh_exp_diff = refresh_payload["exp"] - refresh_payload["iat"]
            assert refresh_exp_diff == 7 * 24 * 3600  # 7 days in seconds

    def test_unique_jti_per_token(self, app, admin_user):
        """Test that each token generation produces unique JWT IDs"""
        with app.app_context():
            tokens1 = JWTManager.generate_tokens(admin_user)
            tokens2 = JWTManager.generate_tokens(admin_user)

            secret_key = app.config["JWT_SECRET_KEY"]
            payload1 = jwt.decode(tokens1["access_token"], secret_key, algorithms=["HS256"])
            payload2 = jwt.decode(tokens2["access_token"], secret_key, algorithms=["HS256"])

            assert payload1["jti"] != payload2["jti"]

    def test_generate_tokens_for_regular_user(self, app, regular_user):
        """Test token generation for non-admin user"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(regular_user)
            secret_key = app.config["JWT_SECRET_KEY"]
            payload = jwt.decode(tokens["access_token"], secret_key, algorithms=["HS256"])

            assert payload["is_admin"] is False
            assert payload["department"] == regular_user.department


class TestJWTTokenVerification:
    """Test token verification functionality"""

    def test_verify_valid_access_token(self, app, admin_user):
        """Test verification of valid access token"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            payload = JWTManager.verify_token(tokens["access_token"], "access")

            assert payload is not None
            assert payload["user_id"] == admin_user.id
            assert payload["type"] == "access"

    def test_verify_valid_refresh_token(self, app, admin_user):
        """Test verification of valid refresh token"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            payload = JWTManager.verify_token(tokens["refresh_token"], "refresh")

            assert payload is not None
            assert payload["user_id"] == admin_user.id
            assert payload["type"] == "refresh"

    def test_verify_token_type_mismatch(self, app, admin_user):
        """Test that token verification fails for wrong token type"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)

            # Try to verify access token as refresh
            result = JWTManager.verify_token(tokens["access_token"], "refresh")
            assert result is None

            # Try to verify refresh token as access
            result = JWTManager.verify_token(tokens["refresh_token"], "access")
            assert result is None

    def test_verify_expired_token(self, app, admin_user):
        """Test that expired tokens are rejected"""
        with app.app_context():
            # Create an expired token manually
            now = datetime.now(UTC)
            payload = {
                "user_id": admin_user.id,
                "type": "access",
                "iat": now - timedelta(hours=2),
                "exp": now - timedelta(hours=1),  # Expired 1 hour ago
            }
            secret_key = app.config["JWT_SECRET_KEY"]
            expired_token = jwt.encode(payload, secret_key, algorithm="HS256")

            result = JWTManager.verify_token(expired_token, "access")
            assert result is None

    def test_verify_invalid_token_string(self, app):
        """Test verification of completely invalid token"""
        with app.app_context():
            result = JWTManager.verify_token("not-a-valid-jwt-token", "access")
            assert result is None

    def test_verify_token_with_wrong_secret(self, app, admin_user):
        """Test that token signed with different secret is rejected"""
        with app.app_context():
            # Create token with different secret
            now = datetime.now(UTC)
            payload = {
                "user_id": admin_user.id,
                "type": "access",
                "iat": now,
                "exp": now + timedelta(minutes=15),
            }
            wrong_secret_token = jwt.encode(payload, "wrong-secret-key", algorithm="HS256")

            result = JWTManager.verify_token(wrong_secret_token, "access")
            assert result is None

    def test_verify_token_with_missing_type(self, app):
        """Test verification of token without type field"""
        with app.app_context():
            now = datetime.now(UTC)
            payload = {
                "user_id": 1,
                "iat": now,
                "exp": now + timedelta(minutes=15),
                # No 'type' field
            }
            secret_key = app.config["JWT_SECRET_KEY"]
            token = jwt.encode(payload, secret_key, algorithm="HS256")

            result = JWTManager.verify_token(token, "access")
            assert result is None

    def test_verify_token_general_exception(self, app):
        """Test token verification handles general exceptions"""
        with app.app_context():
            with patch("auth.jwt_manager.jwt.decode") as mock_decode:
                mock_decode.side_effect = Exception("Unexpected error")
                result = JWTManager.verify_token("some-token", "access")
                assert result is None


class TestJWTRefreshToken:
    """Test token refresh functionality"""

    def test_refresh_with_valid_token(self, app, admin_user):
        """Test successful token refresh"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            new_tokens = JWTManager.refresh_access_token(tokens["refresh_token"])

            assert new_tokens is not None
            assert "access_token" in new_tokens
            assert "refresh_token" in new_tokens
            # New tokens should be different
            assert new_tokens["access_token"] != tokens["access_token"]

    def test_refresh_with_invalid_token(self, app):
        """Test refresh with invalid token returns None"""
        with app.app_context():
            result = JWTManager.refresh_access_token("invalid-refresh-token")
            assert result is None

    def test_refresh_with_access_token_fails(self, app, admin_user):
        """Test that using access token for refresh fails"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            result = JWTManager.refresh_access_token(tokens["access_token"])
            assert result is None

    def test_refresh_for_inactive_user(self, app, db_session):
        """Test refresh fails for inactive user"""
        with app.app_context():
            # Create user and generate token
            user = User(
                name="Inactive Refresh User",
                employee_number="INACTREF001",
                department="IT",
                is_admin=False,
                is_active=True
            )
            user.set_password("password123")
            db_session.add(user)
            db_session.commit()

            tokens = JWTManager.generate_tokens(user)

            # Deactivate user
            user.is_active = False
            db_session.commit()

            # Try to refresh
            result = JWTManager.refresh_access_token(tokens["refresh_token"])
            assert result is None

    def test_refresh_for_deleted_user(self, app, db_session):
        """Test refresh fails for deleted user"""
        with app.app_context():
            # Create user and generate token
            user = User(
                name="Deleted User",
                employee_number="DELUSER001",
                department="IT",
                is_admin=False,
                is_active=True
            )
            user.set_password("password123")
            db_session.add(user)
            db_session.commit()

            tokens = JWTManager.generate_tokens(user)

            # Delete user
            db_session.delete(user)
            db_session.commit()

            # Try to refresh
            result = JWTManager.refresh_access_token(tokens["refresh_token"])
            assert result is None

    def test_refresh_handles_exception(self, app, admin_user):
        """Test refresh handles database exceptions"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)

            with patch("auth.jwt_manager.db.session.get") as mock_get:
                mock_get.side_effect = Exception("Database error")
                result = JWTManager.refresh_access_token(tokens["refresh_token"])
                assert result is None


class TestTokenExtraction:
    """Test token extraction from cookies and headers"""

    def test_extract_token_from_cookie(self, app, admin_user):
        """Test extracting token from HttpOnly cookie"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            with app.test_request_context(
                "/test",
                headers={"Cookie": f"access_token={tokens['access_token']}"}
            ):
                token = JWTManager.extract_token("access")
                assert token == tokens["access_token"]

    def test_extract_refresh_token_from_cookie(self, app, admin_user):
        """Test extracting refresh token from cookie"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            with app.test_request_context(
                "/test",
                headers={"Cookie": f"refresh_token={tokens['refresh_token']}"}
            ):
                token = JWTManager.extract_token("refresh")
                assert token == tokens["refresh_token"]

    def test_extract_token_from_authorization_header(self, app, admin_user):
        """Test extracting access token from Authorization header (fallback)"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            with app.test_request_context(
                "/test",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                token = JWTManager.extract_token("access")
                assert token == tokens["access_token"]

    def test_extract_token_cookie_priority_over_header(self, app, admin_user):
        """Test that cookie has priority over Authorization header"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            cookie_token = "cookie-token"
            with app.test_request_context(
                "/test",
                headers={
                    "Cookie": f"access_token={cookie_token}",
                    "Authorization": f"Bearer {tokens['access_token']}"
                }
            ):
                token = JWTManager.extract_token("access")
                assert token == cookie_token  # Cookie takes priority

    def test_extract_token_no_cookie_or_header(self, app):
        """Test extraction returns None when no token present"""
        with app.app_context():
            with app.test_request_context("/test"):
                token = JWTManager.extract_token("access")
                assert token is None

    def test_extract_refresh_token_no_header_fallback(self, app, admin_user):
        """Test that refresh token extraction doesn't fall back to Authorization header"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            with app.test_request_context(
                "/test",
                headers={"Authorization": f"Bearer {tokens['refresh_token']}"}
            ):
                # Refresh tokens only come from cookies, not Authorization header
                token = JWTManager.extract_token("refresh")
                assert token is None

    def test_extract_token_from_header_method(self, app, admin_user):
        """Test direct header extraction method"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            with app.test_request_context(
                "/test",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                token = JWTManager.extract_token_from_header()
                assert token == tokens["access_token"]

    def test_extract_token_missing_authorization_header(self, app):
        """Test extraction with missing Authorization header"""
        with app.app_context():
            with app.test_request_context("/test"):
                token = JWTManager.extract_token_from_header()
                assert token is None

    def test_extract_token_invalid_scheme(self, app):
        """Test extraction with non-Bearer scheme"""
        with app.app_context():
            with app.test_request_context(
                "/test",
                headers={"Authorization": "Basic some-credentials"}
            ):
                token = JWTManager.extract_token_from_header()
                assert token is None

    def test_extract_token_malformed_header(self, app):
        """Test extraction with malformed Authorization header"""
        with app.app_context():
            with app.test_request_context(
                "/test",
                headers={"Authorization": "InvalidHeaderFormat"}
            ):
                token = JWTManager.extract_token_from_header()
                assert token is None


class TestGetCurrentUser:
    """Test get_current_user functionality"""

    def test_get_current_user_from_cookie(self, app, admin_user):
        """Test getting current user from cookie"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            with app.test_request_context(
                "/test",
                headers={"Cookie": f"access_token={tokens['access_token']}"}
            ):
                user_payload = JWTManager.get_current_user()
                assert user_payload is not None
                assert user_payload["user_id"] == admin_user.id

    def test_get_current_user_from_header(self, app, admin_user):
        """Test getting current user from Authorization header"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            with app.test_request_context(
                "/test",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                user_payload = JWTManager.get_current_user()
                assert user_payload is not None
                assert user_payload["user_id"] == admin_user.id

    def test_get_current_user_no_token(self, app):
        """Test get_current_user returns None when no token"""
        with app.app_context():
            with app.test_request_context("/test"):
                user_payload = JWTManager.get_current_user()
                assert user_payload is None

    def test_get_current_user_invalid_token(self, app):
        """Test get_current_user with invalid token"""
        with app.app_context():
            with app.test_request_context(
                "/test",
                headers={"Authorization": "Bearer invalid-token"}
            ):
                user_payload = JWTManager.get_current_user()
                assert user_payload is None


class TestCSRFTokens:
    """Test CSRF token generation and validation"""

    def test_generate_csrf_token_format(self, app):
        """Test CSRF token has correct format"""
        with app.app_context():
            csrf_token = JWTManager.generate_csrf_token(1, "secret123")
            assert ":" in csrf_token
            parts = csrf_token.split(":")
            assert len(parts) == 2
            assert parts[0].isdigit()  # Timestamp
            assert len(parts[1]) == 32  # Hash

    def test_validate_csrf_token_success(self, app):
        """Test successful CSRF token validation"""
        with app.app_context():
            user_id = 1
            token_secret = "secret123"
            csrf_token = JWTManager.generate_csrf_token(user_id, token_secret)

            result = JWTManager.validate_csrf_token(csrf_token, user_id, token_secret)
            assert result is True

    def test_validate_csrf_token_expired(self, app):
        """Test CSRF token validation fails for expired token"""
        with app.app_context():
            user_id = 1
            token_secret = "secret123"

            # Create token with old timestamp
            old_timestamp = str(int(datetime.now(UTC).timestamp()) - 7200)  # 2 hours ago
            import hashlib
            data = f"{user_id}:{old_timestamp}:{token_secret}"
            token_hash = hashlib.sha256(data.encode()).hexdigest()[:32]
            old_token = f"{old_timestamp}:{token_hash}"

            result = JWTManager.validate_csrf_token(old_token, user_id, token_secret, max_age=3600)
            assert result is False

    def test_validate_csrf_token_wrong_user(self, app):
        """Test CSRF token validation fails for wrong user"""
        with app.app_context():
            csrf_token = JWTManager.generate_csrf_token(1, "secret123")
            result = JWTManager.validate_csrf_token(csrf_token, 2, "secret123")  # Different user
            assert result is False

    def test_validate_csrf_token_wrong_secret(self, app):
        """Test CSRF token validation fails for wrong secret"""
        with app.app_context():
            csrf_token = JWTManager.generate_csrf_token(1, "secret123")
            result = JWTManager.validate_csrf_token(csrf_token, 1, "wrong-secret")
            assert result is False

    def test_validate_csrf_token_missing_colon(self, app):
        """Test CSRF token validation fails for malformed token"""
        with app.app_context():
            result = JWTManager.validate_csrf_token("invalid-token", 1, "secret")
            assert result is False

    def test_validate_csrf_token_invalid_timestamp(self, app):
        """Test CSRF token validation fails for invalid timestamp"""
        with app.app_context():
            result = JWTManager.validate_csrf_token("not-a-number:hash", 1, "secret")
            assert result is False

    def test_validate_csrf_token_with_custom_max_age(self, app):
        """Test CSRF token validation with custom max age"""
        with app.app_context():
            user_id = 1
            token_secret = "secret123"
            csrf_token = JWTManager.generate_csrf_token(user_id, token_secret)

            # Should pass with large max_age
            result = JWTManager.validate_csrf_token(csrf_token, user_id, token_secret, max_age=7200)
            assert result is True


class TestJWTRequiredDecorator:
    """Test jwt_required decorator"""

    def test_jwt_required_with_valid_token(self, app, admin_user):
        """Test decorator allows request with valid token"""
        with app.app_context():

            @jwt_required
            def protected_route():
                from flask import request
                return jsonify({"user_id": request.current_user["user_id"]})

            tokens = JWTManager.generate_tokens(admin_user)
            with app.test_request_context(
                "/test",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response = protected_route()
                data = response[0].get_json() if isinstance(response, tuple) else response.get_json()
                assert data["user_id"] == admin_user.id

    def test_jwt_required_without_token(self, app):
        """Test decorator rejects request without token"""
        with app.app_context():

            @jwt_required
            def protected_route():
                return jsonify({"success": True})

            with app.test_request_context("/test"):
                response, status_code = protected_route()
                data = response.get_json()
                assert status_code == 401
                assert data["error"] == "Authentication required"
                assert data["code"] == "AUTH_REQUIRED"

    def test_jwt_required_with_invalid_token(self, app):
        """Test decorator rejects invalid token"""
        with app.app_context():

            @jwt_required
            def protected_route():
                return jsonify({"success": True})

            with app.test_request_context(
                "/test",
                headers={"Authorization": "Bearer invalid-token"}
            ):
                response, status_code = protected_route()
                assert status_code == 401


class TestAdminRequiredDecorator:
    """Test admin_required decorator"""

    def test_admin_required_with_admin_user(self, app, admin_user):
        """Test decorator allows admin users"""
        with app.app_context():

            @admin_required
            def admin_route():
                from flask import request
                return jsonify({"is_admin": request.current_user["is_admin"]})

            tokens = JWTManager.generate_tokens(admin_user)
            with app.test_request_context(
                "/test",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response = admin_route()
                data = response[0].get_json() if isinstance(response, tuple) else response.get_json()
                assert data["is_admin"] is True

    def test_admin_required_with_regular_user(self, app, regular_user):
        """Test decorator rejects non-admin users"""
        with app.app_context():

            @admin_required
            def admin_route():
                return jsonify({"success": True})

            tokens = JWTManager.generate_tokens(regular_user)
            with app.test_request_context(
                "/test",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response, status_code = admin_route()
                data = response.get_json()
                assert status_code == 403
                assert data["error"] == "Admin privileges required"
                assert data["code"] == "ADMIN_REQUIRED"

    def test_admin_required_without_token(self, app):
        """Test decorator rejects request without token"""
        with app.app_context():

            @admin_required
            def admin_route():
                return jsonify({"success": True})

            with app.test_request_context("/test"):
                response, status_code = admin_route()
                assert status_code == 401


class TestPermissionRequiredDecorator:
    """Test permission_required decorator"""

    def test_permission_required_admin_bypass(self, app, admin_user):
        """Test that admin users bypass permission check"""
        with app.app_context():

            @permission_required("special_permission")
            def permission_route():
                return jsonify({"success": True})

            tokens = JWTManager.generate_tokens(admin_user)
            with app.test_request_context(
                "/test",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response = permission_route()
                data = response[0].get_json() if isinstance(response, tuple) else response.get_json()
                assert data["success"] is True

    def test_permission_required_user_has_permission(self, app, db_session):
        """Test user with required permission is allowed"""
        with app.app_context():
            # Create user with mock permissions
            user = User(
                name="Permission User",
                employee_number="PERM001",
                department="IT",
                is_admin=False,
                is_active=True
            )
            user.set_password("password123")
            db_session.add(user)
            db_session.commit()

            # Mock get_permissions to return specific permission
            with patch.object(user, "get_permissions", return_value=["view_tools"]):
                tokens = JWTManager.generate_tokens(user)

            @permission_required("view_tools")
            def permission_route():
                return jsonify({"success": True})

            with app.test_request_context(
                "/test",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response = permission_route()
                data = response[0].get_json() if isinstance(response, tuple) else response.get_json()
                assert data["success"] is True

    def test_permission_required_user_missing_permission(self, app, regular_user):
        """Test user without required permission is denied"""
        with app.app_context():

            @permission_required("admin_only_permission")
            def permission_route():
                return jsonify({"success": True})

            tokens = JWTManager.generate_tokens(regular_user)
            with app.test_request_context(
                "/test",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response, status_code = permission_route()
                data = response.get_json()
                assert status_code == 403
                assert "admin_only_permission" in data["error"]
                assert data["code"] == "PERMISSION_REQUIRED"

    def test_permission_required_without_token(self, app):
        """Test decorator rejects request without token"""
        with app.app_context():

            @permission_required("any_permission")
            def permission_route():
                return jsonify({"success": True})

            with app.test_request_context("/test"):
                response, status_code = permission_route()
                assert status_code == 401


class TestPermissionRequiredAnyDecorator:
    """Test permission_required_any decorator"""

    def test_permission_required_any_admin_bypass(self, app, admin_user):
        """Test that admin users bypass any permission check"""
        with app.app_context():

            @permission_required_any("perm1", "perm2")
            def any_perm_route():
                return jsonify({"success": True})

            tokens = JWTManager.generate_tokens(admin_user)
            with app.test_request_context(
                "/test",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response = any_perm_route()
                data = response[0].get_json() if isinstance(response, tuple) else response.get_json()
                assert data["success"] is True

    def test_permission_required_any_has_one_permission(self, app, db_session):
        """Test user with one of the required permissions is allowed"""
        with app.app_context():
            user = User(
                name="Any Perm User",
                employee_number="ANYPERM001",
                department="IT",
                is_admin=False,
                is_active=True
            )
            user.set_password("password123")
            db_session.add(user)
            db_session.commit()

            with patch.object(user, "get_permissions", return_value=["perm2"]):
                tokens = JWTManager.generate_tokens(user)

            @permission_required_any("perm1", "perm2", "perm3")
            def any_perm_route():
                return jsonify({"success": True})

            with app.test_request_context(
                "/test",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response = any_perm_route()
                data = response[0].get_json() if isinstance(response, tuple) else response.get_json()
                assert data["success"] is True

    def test_permission_required_any_has_no_permission(self, app, regular_user):
        """Test user without any required permission is denied"""
        with app.app_context():

            @permission_required_any("special1", "special2")
            def any_perm_route():
                return jsonify({"success": True})

            tokens = JWTManager.generate_tokens(regular_user)
            with app.test_request_context(
                "/test",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response, status_code = any_perm_route()
                data = response.get_json()
                assert status_code == 403
                assert "special1, special2" in data["error"]
                assert data["code"] == "PERMISSION_REQUIRED"

    def test_permission_required_any_without_token(self, app):
        """Test decorator rejects request without token"""
        with app.app_context():

            @permission_required_any("perm1", "perm2")
            def any_perm_route():
                return jsonify({"success": True})

            with app.test_request_context("/test"):
                response, status_code = any_perm_route()
                assert status_code == 401


class TestDepartmentRequiredDecorator:
    """Test department_required decorator"""

    def test_department_required_admin_bypass(self, app, admin_user):
        """Test that admin users can access any department"""
        with app.app_context():

            @department_required("Finance")
            def dept_route():
                return jsonify({"success": True})

            tokens = JWTManager.generate_tokens(admin_user)
            with app.test_request_context(
                "/test",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response = dept_route()
                data = response[0].get_json() if isinstance(response, tuple) else response.get_json()
                assert data["success"] is True

    def test_department_required_correct_department(self, app, materials_user):
        """Test user in correct department is allowed"""
        with app.app_context():

            @department_required("Materials")
            def dept_route():
                from flask import request
                return jsonify({"department": request.current_user["department"]})

            tokens = JWTManager.generate_tokens(materials_user)
            with app.test_request_context(
                "/test",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response = dept_route()
                data = response[0].get_json() if isinstance(response, tuple) else response.get_json()
                assert data["department"] == "Materials"

    def test_department_required_wrong_department(self, app, regular_user):
        """Test user in wrong department is denied"""
        with app.app_context():

            @department_required("Finance")
            def dept_route():
                return jsonify({"success": True})

            tokens = JWTManager.generate_tokens(regular_user)  # Engineering department
            with app.test_request_context(
                "/test",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response, status_code = dept_route()
                data = response.get_json()
                assert status_code == 403
                assert "Finance" in data["error"]
                assert data["code"] == "DEPARTMENT_REQUIRED"

    def test_department_required_without_token(self, app):
        """Test decorator rejects request without token"""
        with app.app_context():

            @department_required("IT")
            def dept_route():
                return jsonify({"success": True})

            with app.test_request_context("/test"):
                response, status_code = dept_route()
                assert status_code == 401


class TestCSRFRequiredDecorator:
    """Test csrf_required decorator"""

    def test_csrf_required_get_request_no_check(self, app, admin_user):
        """Test GET requests don't require CSRF token"""
        with app.app_context():

            @csrf_required
            def csrf_route():
                return jsonify({"success": True})

            tokens = JWTManager.generate_tokens(admin_user)
            with app.test_request_context(
                "/test",
                method="GET",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response = csrf_route()
                data = response[0].get_json() if isinstance(response, tuple) else response.get_json()
                assert data["success"] is True

    def test_csrf_required_post_with_valid_token(self, app, admin_user):
        """Test POST request with valid CSRF token succeeds"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)
            payload = JWTManager.verify_token(tokens["access_token"], "access")
            csrf_token = JWTManager.generate_csrf_token(
                payload["user_id"],
                payload["jti"]
            )

            @csrf_required
            def csrf_route():
                return jsonify({"success": True})

            with app.test_request_context(
                "/test",
                method="POST",
                headers={
                    "Authorization": f"Bearer {tokens['access_token']}",
                    "X-CSRF-Token": csrf_token
                }
            ):
                response = csrf_route()
                data = response[0].get_json() if isinstance(response, tuple) else response.get_json()
                assert data["success"] is True

    def test_csrf_required_post_missing_token(self, app, admin_user):
        """Test POST request without CSRF token fails"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)

            @csrf_required
            def csrf_route():
                return jsonify({"success": True})

            with app.test_request_context(
                "/test",
                method="POST",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response, status_code = csrf_route()
                data = response.get_json()
                assert status_code == 403
                assert data["error"] == "CSRF token required"
                assert data["code"] == "CSRF_TOKEN_REQUIRED"

    def test_csrf_required_post_invalid_token(self, app, admin_user):
        """Test POST request with invalid CSRF token fails"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)

            @csrf_required
            def csrf_route():
                return jsonify({"success": True})

            with app.test_request_context(
                "/test",
                method="POST",
                headers={
                    "Authorization": f"Bearer {tokens['access_token']}",
                    "X-CSRF-Token": "invalid:csrf:token"
                }
            ):
                response, status_code = csrf_route()
                data = response.get_json()
                assert status_code == 403
                assert data["error"] == "Invalid CSRF token"
                assert data["code"] == "CSRF_TOKEN_INVALID"

    def test_csrf_required_put_request(self, app, admin_user):
        """Test PUT request requires CSRF token"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)

            @csrf_required
            def csrf_route():
                return jsonify({"success": True})

            with app.test_request_context(
                "/test",
                method="PUT",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response, status_code = csrf_route()
                assert status_code == 403

    def test_csrf_required_delete_request(self, app, admin_user):
        """Test DELETE request requires CSRF token"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)

            @csrf_required
            def csrf_route():
                return jsonify({"success": True})

            with app.test_request_context(
                "/test",
                method="DELETE",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response, status_code = csrf_route()
                assert status_code == 403

    def test_csrf_required_patch_request(self, app, admin_user):
        """Test PATCH request requires CSRF token"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(admin_user)

            @csrf_required
            def csrf_route():
                return jsonify({"success": True})

            with app.test_request_context(
                "/test",
                method="PATCH",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            ):
                response, status_code = csrf_route()
                assert status_code == 403

    def test_csrf_required_without_auth(self, app):
        """Test CSRF decorator requires authentication first"""
        with app.app_context():

            @csrf_required
            def csrf_route():
                return jsonify({"success": True})

            with app.test_request_context("/test", method="POST"):
                response, status_code = csrf_route()
                assert status_code == 401

    def test_csrf_required_fallback_token_secret(self, app, db_session):
        """Test CSRF validation uses fallback when jti is missing"""
        with app.app_context():
            user = User(
                name="CSRF User",
                employee_number="CSRF001",
                department="IT",
                is_admin=False,
                is_active=True
            )
            user.set_password("password123")
            db_session.add(user)
            db_session.commit()

            # Create token without jti (edge case)
            now = datetime.now(UTC)
            payload = {
                "user_id": user.id,
                "user_name": user.name,
                "employee_number": user.employee_number,
                "is_admin": False,
                "department": user.department,
                "permissions": [],
                "iat": now.timestamp(),
                "exp": (now + timedelta(minutes=15)).timestamp(),
                "type": "access"
                # No jti field
            }
            secret_key = app.config["JWT_SECRET_KEY"]
            token = jwt.encode(payload, secret_key, algorithm="HS256")

            # Generate CSRF token with fallback secret
            fallback_secret = f"{user.id}:{payload['iat']}"
            csrf_token = JWTManager.generate_csrf_token(user.id, fallback_secret)

            @csrf_required
            def csrf_route():
                return jsonify({"success": True})

            with app.test_request_context(
                "/test",
                method="POST",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-CSRF-Token": csrf_token
                }
            ):
                response = csrf_route()
                data = response[0].get_json() if isinstance(response, tuple) else response.get_json()
                assert data["success"] is True


class TestDecoratorFunctionNames:
    """Test that decorators preserve function metadata"""

    def test_jwt_required_preserves_name(self):
        """Test jwt_required preserves function name"""

        @jwt_required
        def my_protected_function():
            pass

        assert my_protected_function.__name__ == "my_protected_function"

    def test_admin_required_preserves_name(self):
        """Test admin_required preserves function name"""

        @admin_required
        def my_admin_function():
            pass

        assert my_admin_function.__name__ == "my_admin_function"

    def test_permission_required_preserves_name(self):
        """Test permission_required preserves function name"""

        @permission_required("test")
        def my_permission_function():
            pass

        assert my_permission_function.__name__ == "my_permission_function"

    def test_permission_required_any_preserves_name(self):
        """Test permission_required_any preserves function name"""

        @permission_required_any("test1", "test2")
        def my_any_permission_function():
            pass

        assert my_any_permission_function.__name__ == "my_any_permission_function"

    def test_department_required_preserves_name(self):
        """Test department_required preserves function name"""

        @department_required("IT")
        def my_department_function():
            pass

        assert my_department_function.__name__ == "my_department_function"

    def test_csrf_required_preserves_name(self):
        """Test csrf_required preserves function name"""

        @csrf_required
        def my_csrf_function():
            pass

        assert my_csrf_function.__name__ == "my_csrf_function"


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_permissions_list(self, app, regular_user):
        """Test user with empty permissions list"""
        with app.app_context():
            tokens = JWTManager.generate_tokens(regular_user)
            payload = JWTManager.verify_token(tokens["access_token"], "access")
            assert isinstance(payload["permissions"], list)

    def test_token_with_extra_fields(self, app):
        """Test token with additional unexpected fields still works"""
        with app.app_context():
            now = datetime.now(UTC)
            payload = {
                "user_id": 1,
                "type": "access",
                "iat": now,
                "exp": now + timedelta(minutes=15),
                "extra_field": "unexpected",
                "another_field": {"nested": "data"}
            }
            secret_key = app.config["JWT_SECRET_KEY"]
            token = jwt.encode(payload, secret_key, algorithm="HS256")

            result = JWTManager.verify_token(token, "access")
            assert result is not None
            assert result["extra_field"] == "unexpected"

    def test_very_long_csrf_token_hash(self, app):
        """Test CSRF validation with very long input"""
        with app.app_context():
            long_hash = "a" * 1000
            result = JWTManager.validate_csrf_token(f"12345:{long_hash}", 1, "secret")
            assert result is False

    def test_csrf_token_with_multiple_colons(self, app):
        """Test CSRF token parsing with multiple colons"""
        with app.app_context():
            # Should split only on first colon
            timestamp = str(int(datetime.now(UTC).timestamp()))
            import hashlib
            data = f"1:{timestamp}:secret"
            expected_hash = hashlib.sha256(data.encode()).hexdigest()[:32]
            token = f"{timestamp}:{expected_hash}:extra:parts"

            # This should fail because the hash part includes ":extra:parts"
            result = JWTManager.validate_csrf_token(token, 1, "secret")
            assert result is False
