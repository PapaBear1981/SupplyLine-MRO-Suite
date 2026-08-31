"""Focused regression tests for the central API error boundary."""

from types import SimpleNamespace

from flask import Flask
from werkzeug.exceptions import Conflict, ServiceUnavailable

from utils.error_handler import handle_errors, setup_global_error_handlers


def test_decorator_preserves_http_exception_status_and_contract():
    app = Flask(__name__)
    app.config["TESTING"] = False

    @app.get("/conflict")
    @handle_errors
    def conflict_route():
        raise Conflict()

    response = app.test_client().get("/conflict")

    assert response.status_code == 409
    assert response.json["error_code"] == "conflict"
    assert response.json["reference"] == response.headers["X-Error-Reference"]
    assert response.headers["Cache-Control"] == "no-store"
    assert "debug" not in response.json


def test_global_handler_preserves_unregistered_http_exception():
    app = Flask(__name__)
    app.config["TESTING"] = False
    setup_global_error_handlers(app)

    @app.get("/dependency")
    def dependency_route():
        raise ServiceUnavailable()

    response = app.test_client().get("/dependency")

    assert response.status_code == 503
    assert response.json["error_code"] == "service_unavailable"
    assert response.json["error"] == "The service is temporarily unavailable."


def test_unexpected_decorated_error_rolls_back(monkeypatch):
    rollback_calls = []
    fake_db = SimpleNamespace(session=SimpleNamespace(rollback=lambda: rollback_calls.append(True)))
    monkeypatch.setattr("models.db", fake_db)
    app = Flask(__name__)
    app.config["TESTING"] = False

    @app.get("/broken")
    @handle_errors
    def broken_route():
        raise RuntimeError("sensitive internals")

    response = app.test_client().get("/broken")

    assert response.status_code == 500
    assert rollback_calls == [True]
    assert "sensitive internals" not in response.get_data(as_text=True)
