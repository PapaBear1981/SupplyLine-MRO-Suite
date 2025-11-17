"""
Tests for utils/session_manager.py - Secure Session Manager
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from flask import session

from utils.session_manager import (
    SessionManager,
    csrf_required,
    secure_admin_required,
    secure_login_required,
)


class TestSessionManagerCreateSession:
    """Tests for SessionManager.create_session"""

    def test_create_session_clears_existing(self, app, client, test_user):
        """Test that creating a session clears existing data"""
        with client.session_transaction() as sess:
            sess["old_data"] = "should be cleared"

        with app.test_request_context():
            with client.session_transaction() as sess:
                sess["old_data"] = "should be cleared"

        with app.test_request_context("/", headers={"X-Forwarded-For": "127.0.0.1"}):
            session["old_data"] = "should be cleared"
            SessionManager.create_session(test_user)
            assert "old_data" not in session

    def test_create_session_sets_user_data(self, app, client, test_user):
        """Test that session contains correct user data"""
        with app.test_request_context("/", headers={"X-Forwarded-For": "127.0.0.1"}):
            SessionManager.create_session(test_user)

            assert session["user_id"] == test_user.id
            assert session["user_name"] == test_user.name
            assert session["is_admin"] == test_user.is_admin
            assert session["department"] == test_user.department

    def test_create_session_sets_timestamps(self, app, client, test_user):
        """Test that session contains timestamps"""
        with app.test_request_context("/", headers={"X-Forwarded-For": "127.0.0.1"}):
            SessionManager.create_session(test_user)

            assert "login_time" in session
            assert "last_activity" in session

            # Verify timestamps are valid ISO format
            login_time = datetime.fromisoformat(session["login_time"])
            last_activity = datetime.fromisoformat(session["last_activity"])
            assert isinstance(login_time, datetime)
            assert isinstance(last_activity, datetime)

    def test_create_session_stores_ip_address(self, app, client, test_user):
        """Test that session stores client IP address"""
        with app.test_request_context("/", environ_base={"REMOTE_ADDR": "192.168.1.100"}):
            SessionManager.create_session(test_user)
            assert session["ip_address"] == "192.168.1.100"

    def test_create_session_generates_csrf_token(self, app, client, test_user):
        """Test that session includes CSRF token"""
        with app.test_request_context("/", headers={"X-Forwarded-For": "127.0.0.1"}):
            SessionManager.create_session(test_user)

            assert "csrf_token" in session
            assert len(session["csrf_token"]) == 32  # 16 bytes hex = 32 chars

    def test_create_session_makes_permanent(self, app, client, test_user):
        """Test that session is marked as permanent"""
        with app.test_request_context("/", headers={"X-Forwarded-For": "127.0.0.1"}):
            SessionManager.create_session(test_user)
            assert session.permanent is True


class TestSessionManagerValidateSession:
    """Tests for SessionManager.validate_session"""

    def test_validate_no_session(self, app, client):
        """Test validation fails when no session exists"""
        with app.test_request_context("/"):
            valid, message = SessionManager.validate_session()
            assert valid is False
            assert message == "No active session"

    def test_validate_valid_session(self, app, client, test_user):
        """Test validation passes for valid session"""
        with app.test_request_context("/", environ_base={"REMOTE_ADDR": "127.0.0.1"}):
            SessionManager.create_session(test_user)

            with patch("utils.system_settings.get_session_timeout_value", return_value=30):
                valid, message = SessionManager.validate_session()

            assert valid is True
            assert message == "Valid session"

    def test_validate_expired_session_age(self, app, client, test_user):
        """Test validation fails when session is too old (8+ hours)"""
        with app.test_request_context("/", environ_base={"REMOTE_ADDR": "127.0.0.1"}):
            SessionManager.create_session(test_user)

            # Set login time to 9 hours ago
            old_time = (datetime.utcnow() - timedelta(hours=9)).isoformat()
            session["login_time"] = old_time

            valid, message = SessionManager.validate_session()

            assert valid is False
            assert message == "Session expired"
            # Session should be cleared
            assert "user_id" not in session

    def test_validate_activity_timeout(self, app, client, test_user):
        """Test validation fails when activity timeout exceeded"""
        with app.test_request_context("/", environ_base={"REMOTE_ADDR": "127.0.0.1"}):
            SessionManager.create_session(test_user)

            # Set last activity to more than timeout minutes ago
            old_activity = (datetime.utcnow() - timedelta(minutes=35)).isoformat()
            session["last_activity"] = old_activity

            with patch("utils.system_settings.get_session_timeout_value", return_value=30):
                valid, message = SessionManager.validate_session()

            assert valid is False
            assert "timeout due to inactivity" in message
            # Session should be cleared
            assert "user_id" not in session

    def test_validate_updates_last_activity(self, app, client, test_user):
        """Test that validation updates last_activity timestamp"""
        with app.test_request_context("/", environ_base={"REMOTE_ADDR": "127.0.0.1"}):
            SessionManager.create_session(test_user)

            old_activity = session["last_activity"]

            with patch("utils.system_settings.get_session_timeout_value", return_value=30):
                # Small delay to ensure different timestamp
                valid, message = SessionManager.validate_session()

            assert valid is True
            # last_activity should be updated
            new_activity = session["last_activity"]
            # Should be at least as recent
            old_dt = datetime.fromisoformat(old_activity)
            new_dt = datetime.fromisoformat(new_activity)
            assert new_dt >= old_dt

    def test_validate_invalid_login_time_format(self, app, client, test_user):
        """Test validation handles invalid login_time format"""
        with app.test_request_context("/", environ_base={"REMOTE_ADDR": "127.0.0.1"}):
            SessionManager.create_session(test_user)
            session["login_time"] = "invalid-date"

            valid, message = SessionManager.validate_session()

            assert valid is False
            assert message == "Invalid session data"

    def test_validate_invalid_last_activity_format(self, app, client, test_user):
        """Test validation handles invalid last_activity format"""
        with app.test_request_context("/", environ_base={"REMOTE_ADDR": "127.0.0.1"}):
            SessionManager.create_session(test_user)
            session["last_activity"] = "invalid-date"

            with patch("utils.system_settings.get_session_timeout_value", return_value=30):
                valid, message = SessionManager.validate_session()

            assert valid is False
            assert message == "Invalid session data"

    def test_validate_ip_address_mismatch(self, app, client, test_user):
        """Test validation fails on IP address mismatch when enabled"""
        app.config["SESSION_VALIDATE_IP"] = True

        with app.test_request_context("/", environ_base={"REMOTE_ADDR": "192.168.1.1"}):
            SessionManager.create_session(test_user)

        with app.test_request_context("/", environ_base={"REMOTE_ADDR": "10.0.0.1"}):
            session["user_id"] = test_user.id
            session["ip_address"] = "192.168.1.1"
            session["login_time"] = datetime.utcnow().isoformat()
            session["last_activity"] = datetime.utcnow().isoformat()

            with patch("utils.system_settings.get_session_timeout_value", return_value=30):
                valid, message = SessionManager.validate_session()

            assert valid is False
            assert "IP address mismatch" in message

        # Clean up
        app.config["SESSION_VALIDATE_IP"] = False

    def test_validate_ip_check_disabled_by_default(self, app, client, test_user):
        """Test that IP validation is disabled by default"""
        app.config.pop("SESSION_VALIDATE_IP", None)

        with app.test_request_context("/", environ_base={"REMOTE_ADDR": "192.168.1.1"}):
            SessionManager.create_session(test_user)
            # Change IP but keep session valid otherwise
            session["ip_address"] = "10.0.0.1"

            with patch("utils.system_settings.get_session_timeout_value", return_value=30):
                valid, message = SessionManager.validate_session()

            # Should still be valid because IP check is disabled
            assert valid is True

    def test_validate_minimum_timeout(self, app, client, test_user):
        """Test that timeout is at least 1 minute"""
        with app.test_request_context("/", environ_base={"REMOTE_ADDR": "127.0.0.1"}):
            SessionManager.create_session(test_user)

            # Set timeout to 0 - should be clamped to 1
            with patch("utils.system_settings.get_session_timeout_value", return_value=0):
                # Activity 30 seconds ago should be valid with 1 minute minimum
                session["last_activity"] = (
                    datetime.utcnow() - timedelta(seconds=30)
                ).isoformat()
                valid, message = SessionManager.validate_session()

            assert valid is True


class TestSessionManagerDestroySession:
    """Tests for SessionManager.destroy_session"""

    def test_destroy_clears_session(self, app, client, test_user):
        """Test that destroying session clears all data"""
        with app.test_request_context("/", environ_base={"REMOTE_ADDR": "127.0.0.1"}):
            SessionManager.create_session(test_user)
            assert "user_id" in session

            SessionManager.destroy_session()

            assert "user_id" not in session
            assert "csrf_token" not in session


class TestSessionManagerGenerateCSRFToken:
    """Tests for SessionManager.generate_csrf_token"""

    def test_generate_new_token(self, app, client):
        """Test generating new CSRF token"""
        with app.test_request_context("/"):
            token = SessionManager.generate_csrf_token()

            assert token is not None
            assert len(token) == 32  # 16 bytes hex
            assert session["csrf_token"] == token

    def test_return_existing_token(self, app, client):
        """Test that existing token is returned"""
        with app.test_request_context("/"):
            # Set existing token
            session["csrf_token"] = "existing_token_value"

            token = SessionManager.generate_csrf_token()

            assert token == "existing_token_value"


class TestSessionManagerValidateCSRFToken:
    """Tests for SessionManager.validate_csrf_token"""

    def test_valid_token_from_header(self, app, client):
        """Test validation with token in header"""
        with app.test_request_context(
            "/",
            method="POST",
            headers={"X-CSRF-Token": "valid_token"}
        ):
            session["csrf_token"] = "valid_token"
            result = SessionManager.validate_csrf_token()
            assert result is True

    def test_valid_token_from_form(self, app, client):
        """Test validation with token in form data"""
        with app.test_request_context(
            "/",
            method="POST",
            data={"csrf_token": "valid_token"}
        ):
            session["csrf_token"] = "valid_token"
            result = SessionManager.validate_csrf_token()
            assert result is True

    def test_invalid_token(self, app, client):
        """Test validation with invalid token"""
        with app.test_request_context(
            "/",
            method="POST",
            headers={"X-CSRF-Token": "wrong_token"}
        ):
            session["csrf_token"] = "correct_token"
            result = SessionManager.validate_csrf_token()
            assert result is False

    def test_missing_token(self, app, client):
        """Test validation when token is missing"""
        with app.test_request_context("/", method="POST"):
            session["csrf_token"] = "some_token"
            result = SessionManager.validate_csrf_token()
            # Returns falsy value (None or False) when token not in request
            assert not result

    def test_no_session_token(self, app, client):
        """Test validation when session has no token"""
        with app.test_request_context(
            "/",
            method="POST",
            headers={"X-CSRF-Token": "some_token"}
        ):
            # No csrf_token in session
            result = SessionManager.validate_csrf_token()
            assert result is False


class TestSecureLoginRequiredDecorator:
    """Tests for secure_login_required decorator"""

    def test_valid_session_passes(self, app, client, test_user):
        """Test decorator allows valid session"""
        with app.app_context():
            @app.route("/test_login_required")
            @secure_login_required
            def protected():
                return {"status": "ok"}

            with app.test_request_context("/", environ_base={"REMOTE_ADDR": "127.0.0.1"}):
                SessionManager.create_session(test_user)

                with patch("utils.system_settings.get_session_timeout_value", return_value=30):
                    response = protected()

                assert response == {"status": "ok"}

    def test_invalid_session_returns_401(self, app, client):
        """Test decorator returns 401 for invalid session"""
        @secure_login_required
        def protected():
            return {"status": "ok"}

        with app.test_request_context("/"):
            response, status_code = protected()

            assert status_code == 401
            assert response.json["error"] == "Authentication required"
            assert "reason" in response.json


class TestSecureAdminRequiredDecorator:
    """Tests for secure_admin_required decorator"""

    def test_admin_session_passes(self, app, client, admin_user):
        """Test decorator allows admin session"""
        @secure_admin_required
        def admin_only():
            return {"status": "admin ok"}

        with app.test_request_context("/", environ_base={"REMOTE_ADDR": "127.0.0.1"}):
            SessionManager.create_session(admin_user)

            with patch("utils.system_settings.get_session_timeout_value", return_value=30):
                response = admin_only()

            assert response == {"status": "admin ok"}

    def test_non_admin_returns_403(self, app, client, test_user):
        """Test decorator returns 403 for non-admin"""
        @secure_admin_required
        def admin_only():
            return {"status": "admin ok"}

        with app.test_request_context("/", environ_base={"REMOTE_ADDR": "127.0.0.1"}):
            SessionManager.create_session(test_user)

            with patch("utils.system_settings.get_session_timeout_value", return_value=30):
                response, status_code = admin_only()

            assert status_code == 403
            assert "Admin privileges required" in response.json["error"]

    def test_no_session_returns_401(self, app, client):
        """Test decorator returns 401 when no session"""
        @secure_admin_required
        def admin_only():
            return {"status": "admin ok"}

        with app.test_request_context("/"):
            response, status_code = admin_only()

            assert status_code == 401
            assert response.json["error"] == "Authentication required"


class TestCSRFRequiredDecorator:
    """Tests for csrf_required decorator"""

    def test_get_request_skips_validation(self, app, client):
        """Test GET requests skip CSRF validation"""
        @csrf_required
        def my_view():
            return {"status": "ok"}

        with app.test_request_context("/", method="GET"):
            response = my_view()
            assert response == {"status": "ok"}

    def test_post_with_valid_token(self, app, client):
        """Test POST with valid CSRF token passes"""
        @csrf_required
        def my_view():
            return {"status": "ok"}

        with app.test_request_context(
            "/",
            method="POST",
            headers={"X-CSRF-Token": "valid_token"}
        ):
            session["csrf_token"] = "valid_token"
            response = my_view()
            assert response == {"status": "ok"}

    def test_post_with_invalid_token_returns_403(self, app, client):
        """Test POST with invalid token returns 403"""
        @csrf_required
        def my_view():
            return {"status": "ok"}

        with app.test_request_context(
            "/",
            method="POST",
            headers={"X-CSRF-Token": "wrong_token"}
        ):
            session["csrf_token"] = "correct_token"
            response, status_code = my_view()

            assert status_code == 403
            assert "CSRF token validation failed" in response.json["error"]

    def test_put_requires_csrf(self, app, client):
        """Test PUT requests require CSRF token"""
        @csrf_required
        def my_view():
            return {"status": "ok"}

        with app.test_request_context("/", method="PUT"):
            session["csrf_token"] = "some_token"
            response, status_code = my_view()

            assert status_code == 403

    def test_delete_requires_csrf(self, app, client):
        """Test DELETE requests require CSRF token"""
        @csrf_required
        def my_view():
            return {"status": "ok"}

        with app.test_request_context("/", method="DELETE"):
            session["csrf_token"] = "some_token"
            response, status_code = my_view()

            assert status_code == 403

    def test_missing_token_returns_403(self, app, client):
        """Test missing CSRF token returns 403"""
        @csrf_required
        def my_view():
            return {"status": "ok"}

        with app.test_request_context("/", method="POST"):
            response, status_code = my_view()

            assert status_code == 403
            assert "CSRF" in response.json["error"]
