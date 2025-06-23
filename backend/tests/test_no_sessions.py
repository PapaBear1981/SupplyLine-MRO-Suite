import pytest

from app import create_app
from config import Config
from models import db

import migrate_reorder_fields
import migrate_tool_calibration
import migrate_performance_indexes
import migrate_database_constraints
import app as app_module
from utils import session_cleanup, resource_monitor, logging_utils

# Disable migrations for testing
migrate_reorder_fields.migrate_database = lambda: None
migrate_tool_calibration.migrate_database = lambda: None
migrate_performance_indexes.migrate_database = lambda: None
migrate_database_constraints.migrate_database = lambda: None
app_module.Session = lambda *_args, **_kwargs: None
session_cleanup.init_session_cleanup = lambda *_args, **_kwargs: None
resource_monitor.init_resource_monitoring = lambda *_args, **_kwargs: None
logging_utils.setup_request_logging = lambda *_args, **_kwargs: None

@pytest.fixture(scope="session")
def app():
    Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    Config.SQLALCHEMY_TRACK_MODIFICATIONS = False
    Config.TESTING = True
    Config.SECRET_KEY = "test-secret"
    Config.JWT_SECRET_KEY = "jwt-secret"

    application = create_app()
    application.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    with application.app_context():
        db.create_all()
        yield application
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()

legacy_routes = [
    ("post", "/api/login"),
    ("post", "/api/logout"),
    ("post", "/auth/login"),
    ("post", "/auth/logout"),
    ("get", "/auth/status"),
]

@pytest.mark.parametrize("method, path", legacy_routes)
def test_legacy_session_routes_disabled(client, method, path):
    if method == "post":
        response = client.post(path)
    else:
        response = client.get(path)

    assert response.status_code in (404, 405)
    assert "Set-Cookie" not in response.headers
