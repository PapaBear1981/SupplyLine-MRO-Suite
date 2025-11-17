import pytest
from flask import Flask

from utils.error_handler import (
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    RateLimitError,
    ValidationError,
    _build_error_response,
    _default_message_for_code,
    _status_code_to_error_code,
    handle_errors,
    validate_input,
)


@pytest.fixture
def app():
    flask_app = Flask(__name__)
    flask_app.config.update(TESTING=True)
    return flask_app


class TestErrorCodeMappings:
    def test_status_code_to_error_code_defaults(self):
        assert _status_code_to_error_code(400) == "bad_request"
        assert _status_code_to_error_code(429) == "rate_limit_exceeded"
        assert _status_code_to_error_code(999) == "internal_server_error"

    def test_default_message_for_code(self):
        assert "unexpected error" in _default_message_for_code("internal_server_error")
        assert "problem" in _default_message_for_code("validation_error")
        assert "unexpected" in _default_message_for_code("unknown_code")


class TestBuildErrorResponse:
    def test_build_error_response_includes_debug_when_testing(self, app):
        with app.app_context():
            response, status = _build_error_response(
                message="Boom",
                status_code=500,
                error_code="internal_server_error",
                hint="Check logs",
                reference="ABC123",
                error=ValueError("bad things"),
            )

        assert status == 500
        payload = response.get_json()
        assert payload["error"] == "Boom"
        assert payload["error_code"] == "internal_server_error"
        assert payload["reference"] == "ABC123"
        assert payload["debug"]["type"] == "ValueError"

    def test_build_error_response_excludes_debug_when_not_testing(self):
        app = Flask(__name__)
        with app.app_context():
            response, status = _build_error_response(
                message="No debug",
                status_code=400,
                error_code="bad_request",
                hint="",
                reference=None,
                error=ValueError("hidden"),
            )

        assert status == 400
        payload = response.get_json()
        assert "debug" not in payload
        assert payload["error_code"] == "bad_request"


class TestHandleErrorsDecorator:
    def test_validation_error_response(self, app):
        @handle_errors
        def view_function():
            raise ValidationError("invalid data")

        with app.test_request_context("/"):
            response, status = view_function()

        assert status == 400
        payload = response.get_json()
        assert payload["error_code"] == "validation_error"
        assert payload["error"] == "invalid data"

    def test_authentication_error_response(self, app):
        @handle_errors
        def protected_view():
            raise AuthenticationError("auth needed")

        with app.test_request_context("/"):
            response, status = protected_view()

        assert status == 401
        payload = response.get_json()
        assert payload["error_code"] == "authentication_required"

    def test_authorization_error_response(self, app):
        @handle_errors
        def admin_view():
            raise AuthorizationError("Admin only")

        with app.test_request_context("/"):
            response, status = admin_view()

        assert status == 403
        payload = response.get_json()
        assert payload["error_code"] == "insufficient_permissions"
        assert "Admin only" in payload["hint"]

    def test_rate_limit_error_response(self, app):
        @handle_errors
        def throttled_view():
            raise RateLimitError("Slow down")

        with app.test_request_context("/"):
            response, status = throttled_view()

        assert status == 429
        payload = response.get_json()
        assert payload["error_code"] == "rate_limit_exceeded"
        assert "Slow down" in payload["hint"]

    def test_database_error_response(self, app):
        @handle_errors
        def db_view():
            raise DatabaseError("DB is down")

        with app.test_request_context("/"):
            response, status = db_view()

        assert status == 500
        payload = response.get_json()
        assert payload["error_code"] == "database_error"
        assert "database issue" in payload["error"]


class TestValidateInputHelper:
    def test_validate_input_success(self):
        assert validate_input({"name": "Jane", "id": 1}, ["name", "id"]) is True

    def test_validate_input_missing_required(self):
        with pytest.raises(ValidationError):
            validate_input({"name": "Jane"}, ["name", "id"])

    def test_validate_input_rejects_non_dict(self):
        with pytest.raises(ValidationError):
            validate_input([], ["field"])
