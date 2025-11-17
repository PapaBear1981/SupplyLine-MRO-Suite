"""
Comprehensive tests for utils/logging_utils.py

Tests cover:
- Data sanitization
- Request context handling
- Business event logging
- Security event logging
- Performance metric logging
- Database operation logging
- Performance monitoring decorator
- Correlation ID management
- Request lifecycle logging
- Logger setup and configuration
"""

import logging
import time
import uuid
from unittest.mock import MagicMock, Mock, patch, call

import pytest
from flask import Flask, g, session

from utils.logging_utils import (
    SENSITIVE_FIELDS,
    add_correlation_id,
    get_logger_with_context,
    get_request_context,
    log_business_event,
    log_database_operation,
    log_performance_metric,
    log_request_end,
    log_request_start,
    log_security_event,
    performance_monitor,
    sanitize_data,
    setup_request_logging,
)


class TestSanitizeData:
    """Tests for sanitize_data function."""

    def test_sanitize_dict_with_password(self):
        """Test that password fields are redacted."""
        data = {"username": "john", "password": "secret123"}
        result = sanitize_data(data)
        assert result["username"] == "john"
        assert result["password"] == "***REDACTED***"

    def test_sanitize_dict_with_token(self):
        """Test that token fields are redacted."""
        data = {"user_id": 1, "access_token": "abc123xyz"}
        result = sanitize_data(data)
        assert result["user_id"] == 1
        assert result["access_token"] == "***REDACTED***"

    def test_sanitize_dict_with_multiple_sensitive_fields(self):
        """Test redaction of multiple sensitive fields."""
        data = {
            "name": "John Doe",
            "password": "secret",
            "api_key": "key123",
            "secret_code": "classified",
            "email": "john@example.com",
            "ssn": "123-45-6789"
        }
        result = sanitize_data(data)
        assert result["name"] == "John Doe"
        assert result["password"] == "***REDACTED***"
        assert result["api_key"] == "***REDACTED***"
        assert result["secret_code"] == "***REDACTED***"
        assert result["email"] == "***REDACTED***"
        assert result["ssn"] == "***REDACTED***"

    def test_sanitize_nested_dict(self):
        """Test sanitization of nested dictionaries."""
        data = {
            "user": {
                "name": "Alice",
                "settings": {
                    "password": "pass123",
                    "auth_token": "token456"
                }
            }
        }
        result = sanitize_data(data)
        assert result["user"]["name"] == "Alice"
        assert result["user"]["settings"]["password"] == "***REDACTED***"
        assert result["user"]["settings"]["auth_token"] == "***REDACTED***"

    def test_sanitize_list_of_dicts(self):
        """Test sanitization of lists containing dictionaries."""
        data = [
            {"user": "john", "password": "pass1"},
            {"user": "jane", "password": "pass2"}
        ]
        result = sanitize_data(data)
        assert result[0]["user"] == "john"
        assert result[0]["password"] == "***REDACTED***"
        assert result[1]["user"] == "jane"
        assert result[1]["password"] == "***REDACTED***"

    def test_sanitize_list_with_mixed_types(self):
        """Test sanitization of lists with mixed types."""
        data = [
            {"name": "test", "token": "secret"},
            "plain string",
            123,
            ["nested", "list"]
        ]
        result = sanitize_data(data)
        assert result[0]["name"] == "test"
        assert result[0]["token"] == "***REDACTED***"
        assert result[1] == "plain string"
        assert result[2] == 123
        assert result[3] == ["nested", "list"]

    def test_sanitize_long_string(self):
        """Test truncation of very long strings."""
        long_string = "x" * 200
        result = sanitize_data(long_string)
        assert len(result) == 100 + len("...[truncated]")
        assert result.endswith("...[truncated]")

    def test_sanitize_string_under_100_chars(self):
        """Test that short strings are not truncated."""
        short_string = "This is a short string"
        result = sanitize_data(short_string)
        assert result == short_string

    def test_sanitize_string_exactly_100_chars(self):
        """Test string at boundary."""
        exactly_100 = "x" * 100
        result = sanitize_data(exactly_100)
        assert result == exactly_100

    def test_sanitize_primitive_types(self):
        """Test that primitive types are returned unchanged."""
        assert sanitize_data(123) == 123
        assert sanitize_data(45.67) == 45.67
        assert sanitize_data(True) is True
        assert sanitize_data(False) is False
        assert sanitize_data(None) is None

    def test_sanitize_empty_dict(self):
        """Test sanitization of empty dictionary."""
        assert sanitize_data({}) == {}

    def test_sanitize_empty_list(self):
        """Test sanitization of empty list."""
        assert sanitize_data([]) == []

    def test_sanitize_case_insensitive(self):
        """Test that sensitive field matching is case-insensitive."""
        data = {
            "PASSWORD": "secret",
            "Token": "abc",
            "API_KEY": "key123"
        }
        result = sanitize_data(data)
        assert result["PASSWORD"] == "***REDACTED***"
        assert result["Token"] == "***REDACTED***"
        assert result["API_KEY"] == "***REDACTED***"

    def test_sanitize_partial_match(self):
        """Test that partial matches are redacted."""
        data = {
            "user_password_hash": "hash123",
            "auth_token_expiry": "2024-01-01",
            "reset_code": "12345"
        }
        result = sanitize_data(data)
        assert result["user_password_hash"] == "***REDACTED***"
        assert result["auth_token_expiry"] == "***REDACTED***"
        assert result["reset_code"] == "***REDACTED***"

    def test_all_sensitive_fields_covered(self):
        """Test that all defined sensitive fields are properly sanitized."""
        # Create a dict with all sensitive fields
        data = {field: f"value_{field}" for field in SENSITIVE_FIELDS}
        result = sanitize_data(data)
        for field in SENSITIVE_FIELDS:
            assert result[field] == "***REDACTED***", f"Field {field} was not redacted"


class TestGetRequestContext:
    """Tests for get_request_context function."""

    def test_context_without_request(self, app):
        """Test context generation without active request."""
        with app.app_context():
            context = get_request_context()
            assert "correlation_id" in context
            assert "timestamp" in context
            assert isinstance(context["timestamp"], float)
            # Should not have request-specific fields
            assert "method" not in context
            assert "path" not in context

    def test_context_with_request(self, app):
        """Test context generation with active request."""
        with app.test_request_context("/test", method="POST"):
            g.correlation_id = "test-corr-id"
            context = get_request_context()
            assert context["correlation_id"] == "test-corr-id"
            assert context["method"] == "POST"
            assert context["path"] == "/test"
            assert "ip_address" in context
            assert "user_agent" in context

    def test_context_with_user_session(self, app):
        """Test context generation with user session data."""
        with app.test_request_context("/test"):
            session["user_id"] = 42
            session["name"] = "Test User"
            session["department"] = "Engineering"
            context = get_request_context()
            assert context["user_id"] == 42
            assert context["user_name"] == "Test User"
            assert context["user_department"] == "Engineering"

    def test_context_without_correlation_id(self, app):
        """Test context when correlation_id is not set."""
        with app.test_request_context("/test"):
            context = get_request_context()
            assert context["correlation_id"] is None

    def test_context_truncates_user_agent(self, app):
        """Test that user agent is truncated if too long."""
        long_ua = "Mozilla/5.0 " + "x" * 200
        with app.test_request_context("/test", headers={"User-Agent": long_ua}):
            context = get_request_context()
            assert len(context["user_agent"]) == 100

    def test_context_without_user_agent(self, app):
        """Test context when User-Agent header is missing."""
        with app.test_request_context("/test"):
            context = get_request_context()
            assert context["user_agent"] == ""


class TestLogBusinessEvent:
    """Tests for log_business_event function."""

    def test_log_business_event_info_level(self, app):
        """Test logging business event at info level."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_business_event("USER_CREATED", {"name": "John"}, user_id=1)

                mock_get_logger.assert_called_with("business_events")
                mock_logger.info.assert_called_once()
                call_args = mock_logger.info.call_args
                assert "Business event: USER_CREATED" in call_args[0][0]

    def test_log_business_event_warning_level(self, app):
        """Test logging business event at warning level."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_business_event("LOW_STOCK", {"item": "widget"}, level="warning")

                mock_logger.warning.assert_called_once()

    def test_log_business_event_error_level(self, app):
        """Test logging business event at error level."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_business_event("SYSTEM_FAILURE", {"module": "auth"}, level="error")

                mock_logger.error.assert_called_once()

    def test_log_business_event_critical_level(self, app):
        """Test logging business event at critical level."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_business_event("DATA_BREACH", {"severity": "high"}, level="critical")

                mock_logger.critical.assert_called_once()

    def test_log_business_event_debug_level(self, app):
        """Test logging business event at debug level."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_business_event("DEBUG_INFO", {"data": "test"}, level="debug")

                mock_logger.debug.assert_called_once()

    def test_log_business_event_invalid_level(self, app):
        """Test logging business event with invalid level defaults to info."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_business_event("TEST_EVENT", {"data": "test"}, level="invalid_level")

                # Should warn about invalid level then log at info
                mock_logger.warning.assert_called_once()
                mock_logger.info.assert_called_once()

    def test_log_business_event_sanitizes_data(self, app):
        """Test that sensitive data is sanitized."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_business_event("USER_LOGIN", {
                    "username": "john",
                    "password": "secret123"
                })

                call_kwargs = mock_logger.info.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["details"]["password"] == "***REDACTED***"
                assert extra["details"]["username"] == "john"

    def test_log_business_event_uses_session_user_id(self, app):
        """Test that session user_id is used when not provided."""
        with app.test_request_context("/test"):
            session["user_id"] = 99
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_business_event("TEST_EVENT", {"data": "test"})

                call_kwargs = mock_logger.info.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["user_id"] == 99

    def test_log_business_event_explicit_user_id_when_no_session(self, app):
        """Test that explicit user_id is used when no session user."""
        with app.test_request_context("/test"):
            # No session user_id set
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_business_event("TEST_EVENT", {"data": "test"}, user_id=42)

                call_kwargs = mock_logger.info.call_args[1]
                extra = call_kwargs["extra"]
                # The explicit user_id parameter is used when no session user exists
                assert extra["user_id"] == 42


class TestLogSecurityEvent:
    """Tests for log_security_event function."""

    def test_log_security_event_warning(self, app):
        """Test logging security event at warning level."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_security_event("FAILED_LOGIN", {"attempts": 3})

                mock_get_logger.assert_called_with("security_events")
                mock_logger.warning.assert_called_once()

    def test_log_security_event_error(self, app):
        """Test logging security event at error level."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_security_event("UNAUTHORIZED_ACCESS", {"resource": "/admin"}, severity="error")

                mock_logger.error.assert_called_once()

    def test_log_security_event_critical(self, app):
        """Test logging security event at critical level."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_security_event("BREACH_DETECTED", {"type": "SQL injection"}, severity="critical")

                mock_logger.critical.assert_called_once()

    def test_log_security_event_info(self, app):
        """Test logging security event at info level."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_security_event("USER_LOGOUT", {"user_id": 1}, severity="info")

                mock_logger.info.assert_called_once()

    def test_log_security_event_includes_security_flag(self, app):
        """Test that security_event flag is set to True."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_security_event("TEST", {"data": "test"})

                call_kwargs = mock_logger.warning.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["security_event"] is True

    def test_log_security_event_sanitizes_data(self, app):
        """Test that sensitive data is sanitized in security logs."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_security_event("LOGIN_ATTEMPT", {
                    "username": "admin",
                    "password": "wrongpassword"
                })

                call_kwargs = mock_logger.warning.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["details"]["password"] == "***REDACTED***"


class TestLogPerformanceMetric:
    """Tests for log_performance_metric function."""

    def test_log_fast_operation_debug_level(self, app):
        """Test that fast operations are logged at debug level."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_performance_metric("quick_query", 50.0)

                mock_get_logger.assert_called_with("performance")
                mock_logger.debug.assert_called_once()
                assert "50.00ms" in mock_logger.debug.call_args[0][0]

    def test_log_medium_operation_info_level(self, app):
        """Test that medium operations are logged at info level."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_performance_metric("medium_operation", 1500.0)

                mock_logger.info.assert_called_once()

    def test_log_slow_operation_warning_level(self, app):
        """Test that slow operations are logged at warning level."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_performance_metric("slow_operation", 6000.0)

                mock_logger.warning.assert_called_once()

    def test_log_performance_metric_with_details(self, app):
        """Test logging performance metric with additional details."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_performance_metric("api_call", 100.0, {"endpoint": "/users", "count": 10})

                call_kwargs = mock_logger.debug.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["details"]["endpoint"] == "/users"
                assert extra["details"]["count"] == 10

    def test_log_performance_metric_without_details(self, app):
        """Test logging performance metric without additional details."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_performance_metric("simple_operation", 25.0)

                call_kwargs = mock_logger.debug.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["details"] == {}

    def test_log_performance_metric_rounds_duration(self, app):
        """Test that duration is rounded to 2 decimal places."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_performance_metric("test", 123.456789)

                call_kwargs = mock_logger.debug.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["duration_ms"] == 123.46

    def test_log_performance_metric_boundary_1000ms(self, app):
        """Test boundary at exactly 1000ms."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_performance_metric("test", 1000.0)

                # 1000ms is not > 1000, so should be debug
                mock_logger.debug.assert_called_once()

    def test_log_performance_metric_boundary_5000ms(self, app):
        """Test boundary at exactly 5000ms."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_performance_metric("test", 5000.0)

                # 5000ms is not > 5000, so should be info
                mock_logger.info.assert_called_once()


class TestLogDatabaseOperation:
    """Tests for log_database_operation function."""

    def test_log_fast_db_operation_debug_level(self, app):
        """Test fast database operations logged at debug level."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_database_operation("SELECT", "users", 50.0, 10)

                mock_get_logger.assert_called_with("database")
                mock_logger.debug.assert_called_once()
                # Check that the format string and arguments are correct
                call_args = mock_logger.debug.call_args[0]
                assert "Database operation" in call_args[0]
                assert call_args[1] == "SELECT"
                assert call_args[2] == "users"

    def test_log_medium_db_operation_info_level(self, app):
        """Test medium database operations logged at info level."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_database_operation("UPDATE", "products", 750.0, 5)

                mock_logger.info.assert_called_once()

    def test_log_slow_db_operation_warning_level(self, app):
        """Test slow database operations logged at warning level."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_database_operation("INSERT", "orders", 1500.0, 100)

                mock_logger.warning.assert_called_once()
                assert "Slow database operation" in mock_logger.warning.call_args[0][0]

    def test_log_db_operation_includes_affected_rows(self, app):
        """Test that affected_rows is included in log data."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_database_operation("DELETE", "old_logs", 100.0, 1000)

                call_kwargs = mock_logger.debug.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["affected_rows"] == 1000

    def test_log_db_operation_without_affected_rows(self, app):
        """Test database operation logging without affected_rows."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_database_operation("SELECT", "config", 25.0)

                call_kwargs = mock_logger.debug.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["affected_rows"] is None

    def test_log_db_operation_rounds_duration(self, app):
        """Test that duration is rounded to 2 decimal places."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_database_operation("SELECT", "users", 123.456789)

                call_kwargs = mock_logger.debug.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["duration_ms"] == 123.46

    def test_log_db_operation_boundary_500ms(self, app):
        """Test boundary at exactly 500ms."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_database_operation("SELECT", "test", 500.0)

                # 500ms is not > 500, so should be debug
                mock_logger.debug.assert_called_once()

    def test_log_db_operation_boundary_1000ms(self, app):
        """Test boundary at exactly 1000ms."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_database_operation("SELECT", "test", 1000.0)

                # 1000ms is not > 1000, so should be info
                mock_logger.info.assert_called_once()


class TestPerformanceMonitor:
    """Tests for performance_monitor decorator."""

    def test_decorator_successful_execution(self, app):
        """Test decorator logs successful execution."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.log_performance_metric") as mock_log:
                @performance_monitor("test_operation")
                def test_func():
                    return "success"

                result = test_func()
                assert result == "success"
                mock_log.assert_called_once()
                call_args = mock_log.call_args
                assert call_args[0][0] == "test_operation"
                assert call_args[0][2]["success"] is True

    def test_decorator_with_exception(self, app):
        """Test decorator logs failed execution."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.log_performance_metric") as mock_log:
                @performance_monitor("failing_operation")
                def failing_func():
                    raise ValueError("Test error")

                with pytest.raises(ValueError, match="Test error"):
                    failing_func()

                mock_log.assert_called_once()
                call_args = mock_log.call_args
                assert call_args[0][2]["success"] is False
                assert call_args[0][2]["error_type"] == "ValueError"
                assert "Test error" in call_args[0][2]["error_message"]

    def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves function metadata."""
        @performance_monitor("test")
        def documented_func():
            """This is a test function."""
            pass

        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "This is a test function."

    def test_decorator_with_args_and_kwargs(self, app):
        """Test decorator works with function arguments."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.log_performance_metric"):
                @performance_monitor("args_test")
                def func_with_args(a, b, c=None):
                    return a + b + (c or 0)

                result = func_with_args(1, 2, c=3)
                assert result == 6

    def test_decorator_measures_duration(self, app):
        """Test that decorator accurately measures duration."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.log_performance_metric") as mock_log:
                @performance_monitor("timed_operation")
                def slow_func():
                    time.sleep(0.01)  # 10ms
                    return "done"

                slow_func()
                call_args = mock_log.call_args
                duration = call_args[0][1]
                # Should be at least 10ms
                assert duration >= 10.0


class TestAddCorrelationId:
    """Tests for add_correlation_id function."""

    def test_adds_new_correlation_id(self, app):
        """Test that correlation ID is added when not present."""
        with app.test_request_context("/test"):
            corr_id = add_correlation_id()
            assert hasattr(g, "correlation_id")
            assert g.correlation_id == corr_id
            # Should be a valid UUID
            uuid.UUID(corr_id)

    def test_returns_existing_correlation_id(self, app):
        """Test that existing correlation ID is returned."""
        with app.test_request_context("/test"):
            g.correlation_id = "existing-id"
            corr_id = add_correlation_id()
            assert corr_id == "existing-id"

    def test_correlation_id_is_uuid_format(self, app):
        """Test that generated correlation ID is a valid UUID."""
        with app.test_request_context("/test"):
            corr_id = add_correlation_id()
            # This will raise an exception if not valid UUID
            parsed_uuid = uuid.UUID(corr_id)
            assert str(parsed_uuid) == corr_id


class TestLogRequestStart:
    """Tests for log_request_start function."""

    def test_logs_request_start(self, app):
        """Test that request start is logged."""
        with app.test_request_context("/api/test", method="POST"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_request_start()

                mock_get_logger.assert_called_with("requests")
                mock_logger.info.assert_called_once()
                assert "Request started" in mock_logger.info.call_args[0][0]

    def test_sets_start_time(self, app):
        """Test that start time is set on g object."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger"):
                log_request_start()
                assert hasattr(g, "start_time")
                assert isinstance(g.start_time, float)

    def test_adds_correlation_id(self, app):
        """Test that correlation ID is added."""
        with app.test_request_context("/test"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_request_start()

                assert hasattr(g, "correlation_id")
                call_kwargs = mock_logger.info.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["correlation_id"] == g.correlation_id

    def test_logs_request_details(self, app):
        """Test that request details are logged."""
        with app.test_request_context("/api/users", method="GET"):
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_request_start()

                call_kwargs = mock_logger.info.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["method"] == "GET"
                assert extra["path"] == "/api/users"
                assert "ip_address" in extra

    def test_logs_user_id_from_session(self, app):
        """Test that user_id from session is logged."""
        with app.test_request_context("/test"):
            session["user_id"] = 123
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                log_request_start()

                call_kwargs = mock_logger.info.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["user_id"] == 123


class TestLogRequestEnd:
    """Tests for log_request_end function."""

    def test_logs_request_end_with_start_time(self, app):
        """Test that request end is logged when start_time exists."""
        with app.test_request_context("/test"):
            g.start_time = time.time() - 0.1  # 100ms ago
            g.correlation_id = "test-corr-id"
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                response = Mock()
                response.status_code = 200

                result = log_request_end(response)

                assert result == response
                mock_get_logger.assert_called_with("requests")
                mock_logger.info.assert_called_once()
                assert "Request completed" in mock_logger.info.call_args[0][0]

    def test_returns_response_without_start_time(self, app):
        """Test that response is returned even without start_time."""
        with app.test_request_context("/test"):
            response = Mock()
            response.status_code = 404

            result = log_request_end(response)

            assert result == response

    def test_logs_duration(self, app):
        """Test that duration is calculated and logged."""
        with app.test_request_context("/test"):
            g.start_time = time.time() - 0.05  # 50ms ago
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                response = Mock()
                response.status_code = 200

                log_request_end(response)

                call_kwargs = mock_logger.info.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["duration_ms"] >= 50.0
                assert isinstance(extra["duration_ms"], float)

    def test_logs_status_code(self, app):
        """Test that response status code is logged."""
        with app.test_request_context("/test"):
            g.start_time = time.time()
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                response = Mock()
                response.status_code = 500

                log_request_end(response)

                call_kwargs = mock_logger.info.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["status_code"] == 500

    def test_logs_correlation_id(self, app):
        """Test that correlation ID is included in log."""
        with app.test_request_context("/test"):
            g.start_time = time.time()
            g.correlation_id = "test-123"
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                response = Mock()
                response.status_code = 200

                log_request_end(response)

                call_kwargs = mock_logger.info.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["correlation_id"] == "test-123"

    def test_logs_user_id_from_session(self, app):
        """Test that user_id from session is logged."""
        with app.test_request_context("/test"):
            session["user_id"] = 456
            g.start_time = time.time()
            with patch("utils.logging_utils.logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                response = Mock()
                response.status_code = 200

                log_request_end(response)

                call_kwargs = mock_logger.info.call_args[1]
                extra = call_kwargs["extra"]
                assert extra["user_id"] == 456


class TestSetupRequestLogging:
    """Tests for setup_request_logging function."""

    def test_registers_before_request_handler(self):
        """Test that before_request handler is registered."""
        test_app = Flask(__name__)
        test_app.config["SECRET_KEY"] = "test-key"

        with patch("utils.logging_utils.log_request_start") as mock_start:
            setup_request_logging(test_app)

            # Verify handlers are registered
            assert len(test_app.before_request_funcs[None]) > 0

    def test_registers_after_request_handler(self):
        """Test that after_request handler is registered."""
        test_app = Flask(__name__)
        test_app.config["SECRET_KEY"] = "test-key"

        setup_request_logging(test_app)

        # Verify after_request handlers are registered
        assert len(test_app.after_request_funcs[None]) > 0

    def test_logs_configuration_message(self):
        """Test that configuration message is logged."""
        test_app = Flask(__name__)
        test_app.config["SECRET_KEY"] = "test-key"

        with patch("utils.logging_utils.logger") as mock_logger:
            setup_request_logging(test_app)

            mock_logger.info.assert_called_once_with("Request logging middleware configured")

    def test_middleware_calls_log_request_start(self):
        """Test that middleware calls log_request_start."""
        test_app = Flask(__name__)
        test_app.config["SECRET_KEY"] = "test-key"

        @test_app.route("/test")
        def test_route():
            return "OK"

        with patch("utils.logging_utils.log_request_start") as mock_start:
            with patch("utils.logging_utils.log_request_end") as mock_end:
                # Ensure mock_end returns the response
                mock_end.side_effect = lambda r: r
                setup_request_logging(test_app)

                with test_app.test_client() as client:
                    client.get("/test")

                mock_start.assert_called_once()

    def test_middleware_calls_log_request_end(self):
        """Test that middleware calls log_request_end."""
        test_app = Flask(__name__)
        test_app.config["SECRET_KEY"] = "test-key"

        @test_app.route("/test")
        def test_route():
            return "OK"

        with patch("utils.logging_utils.log_request_start"):
            with patch("utils.logging_utils.log_request_end") as mock_end:
                mock_end.side_effect = lambda r: r
                setup_request_logging(test_app)

                with test_app.test_client() as client:
                    client.get("/test")

                mock_end.assert_called_once()


class TestGetLoggerWithContext:
    """Tests for get_logger_with_context function."""

    def test_returns_logger_instance(self):
        """Test that a logger instance is returned."""
        logger = get_logger_with_context("test_logger")
        assert isinstance(logger, logging.Logger)

    def test_returns_logger_with_correct_name(self):
        """Test that logger has the specified name."""
        logger = get_logger_with_context("my_module")
        assert logger.name == "my_module"

    def test_returns_same_logger_for_same_name(self):
        """Test that same logger instance is returned for same name."""
        logger1 = get_logger_with_context("shared_logger")
        logger2 = get_logger_with_context("shared_logger")
        assert logger1 is logger2

    def test_returns_different_loggers_for_different_names(self):
        """Test that different logger instances are returned for different names."""
        logger1 = get_logger_with_context("logger_a")
        logger2 = get_logger_with_context("logger_b")
        assert logger1 is not logger2
        assert logger1.name != logger2.name
