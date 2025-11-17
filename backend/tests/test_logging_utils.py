import logging

from flask import Flask, session

from utils.logging_utils import (
    get_request_context,
    log_business_event,
    sanitize_data,
)


def test_sanitize_data_redacts_and_truncates():
    data = {
        "password": "secret123",
        "profile": {"token": "abc", "name": "User"},
        "emails": ["user@example.com"],
        "description": "a" * 120,
    }

    sanitized = sanitize_data(data)

    assert sanitized["password"] == "***REDACTED***"
    assert sanitized["profile"]["token"] == "***REDACTED***"
    assert sanitized["emails"] == "***REDACTED***"
    assert sanitized["description"].endswith("...[truncated]")


def test_get_request_context_with_session_information():
    app = Flask(__name__)
    app.secret_key = "test-key"

    with app.test_request_context(
        "/example",
        method="POST",
        headers={"User-Agent": "pytest-agent"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    ):
        session["user_id"] = 42
        session["name"] = "Tester"
        session["department"] = "QA"

        context = get_request_context()

    assert context["method"] == "POST"
    assert context["path"] == "/example"
    assert context["ip_address"] == "127.0.0.1"
    assert context["user_id"] == 42
    assert context["user_department"] == "QA"
    assert "timestamp" in context


def test_log_business_event_invalid_level_defaults_to_info(caplog):
    caplog.set_level(logging.INFO, logger="business_events")

    log_business_event("sample", {"password": "secret"}, level="INVALID")

    records = [record for record in caplog.records if record.name == "business_events"]
    assert any(record.levelname == "WARNING" for record in records)
    assert any(record.levelname == "INFO" for record in records)
    assert any(getattr(record, "invalid_level", None) == "INVALID" for record in records)
