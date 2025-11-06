"""
Test for Issue #413: Outdated Dependencies with Known Vulnerabilities
Ensures that updated dependencies can be imported and have correct versions
"""

from importlib.metadata import version as get_version

import pytest


def test_flask_version():
    """Test that Flask is updated to 3.1.1 or higher (fixes CVE-2025-47278)"""
    import flask
    version = tuple(map(int, flask.__version__.split(".")[:3]))
    assert version >= (3, 1, 1), f"Flask version should be 3.1.1 or higher, got {flask.__version__}"


def test_werkzeug_version():
    """Test that Werkzeug is updated to 3.1.3 or higher (fixes CVE-2023-25577, CVE-2023-46136)"""
    werkzeug_version = get_version("werkzeug")
    version = tuple(map(int, werkzeug_version.split(".")[:3]))
    assert version >= (3, 1, 3), f"Werkzeug version should be 3.1.3 or higher, got {werkzeug_version}"


def test_sqlalchemy_version():
    """Test that SQLAlchemy is updated to 2.0.x"""
    import sqlalchemy
    version = tuple(map(int, sqlalchemy.__version__.split(".")[:2]))
    assert version >= (2, 0), f"SQLAlchemy version should be 2.0.x or higher, got {sqlalchemy.__version__}"


def test_pyjwt_version():
    """Test that PyJWT is updated to 2.10.1 or higher"""
    import jwt
    # PyJWT version is in jwt.__version__
    version_str = jwt.__version__
    # Parse version (e.g., "2.10.1")
    version_parts = version_str.split(".")
    major = int(version_parts[0])
    minor = int(version_parts[1])

    assert major >= 2, f"PyJWT major version should be 2 or higher, got {version_str}"
    if major == 2:
        assert minor >= 10, f"PyJWT minor version should be 10 or higher for v2.x, got {version_str}"


def test_flask_sqlalchemy_version():
    """Test that Flask-SQLAlchemy is updated to 3.1.x"""
    import flask_sqlalchemy
    version = tuple(map(int, flask_sqlalchemy.__version__.split(".")[:2]))
    assert version >= (3, 1), f"Flask-SQLAlchemy version should be 3.1.x or higher, got {flask_sqlalchemy.__version__}"


def test_gunicorn_version():
    """Test that gunicorn is updated to 23.0.0 or higher"""
    try:
        import gunicorn
        version = tuple(map(int, gunicorn.__version__.split(".")[:2]))
        assert version >= (23, 0), f"gunicorn version should be 23.0.0 or higher, got {gunicorn.__version__}"
    except ImportError:
        pytest.skip("gunicorn not installed (may not be needed in test environment)")


def test_psutil_version():
    """Test that psutil is updated to 6.1.1 or higher"""
    import psutil
    version = tuple(map(int, psutil.__version__.split(".")[:2]))
    assert version >= (6, 1), f"psutil version should be 6.1.x or higher, got {psutil.__version__}"


def test_reportlab_version():
    """Test that reportlab is updated to 4.2.5 or higher"""
    import reportlab
    version_str = reportlab.Version
    version_parts = version_str.split(".")
    major = int(version_parts[0])
    minor = int(version_parts[1])

    assert major >= 4, f"reportlab major version should be 4 or higher, got {version_str}"
    if major == 4:
        assert minor >= 2, f"reportlab minor version should be 2 or higher for v4.x, got {version_str}"


def test_openpyxl_version():
    """Test that openpyxl is updated to 3.1.5 or higher"""
    import openpyxl
    version = tuple(map(int, openpyxl.__version__.split(".")[:3]))
    assert version >= (3, 1, 5), f"openpyxl version should be 3.1.5 or higher, got {openpyxl.__version__}"


def test_all_dependencies_importable():
    """Test that all critical dependencies can be imported"""
    critical_imports = [
        "flask",
        "werkzeug",
        "sqlalchemy",
        "flask_sqlalchemy",
        "flask_session",
        "flask_cors",
        "jwt",  # PyJWT
        "psutil",
        "reportlab",
        "openpyxl",
        "pytest",
    ]

    failed_imports = []
    for module_name in critical_imports:
        try:
            __import__(module_name)
        except ImportError as e:
            failed_imports.append((module_name, str(e)))

    assert len(failed_imports) == 0, f"Failed to import: {failed_imports}"


def test_flask_app_can_be_created():
    """Test that a Flask app can be created with updated dependencies"""
    from flask import Flask

    app = Flask(__name__)
    assert app is not None
    assert hasattr(app, "route")
    assert hasattr(app, "config")


def test_sqlalchemy_can_create_engine():
    """Test that SQLAlchemy can create a database engine"""
    import sqlalchemy
    from sqlalchemy import create_engine

    # Create in-memory SQLite engine for testing
    engine = create_engine("sqlite:///:memory:")
    assert engine is not None

    # Test connection
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT 1"))
        assert result.fetchone()[0] == 1


def test_jwt_can_encode_decode():
    """Test that PyJWT can encode and decode tokens"""
    import jwt

    payload = {"user_id": 123, "username": "test"}
    secret = "test-secret-key"

    # Encode
    token = jwt.encode(payload, secret, algorithm="HS256")
    assert token is not None

    # Decode
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
    assert decoded["user_id"] == 123
    assert decoded["username"] == "test"


def test_no_known_vulnerabilities():
    """
    Test that we're not using versions with known vulnerabilities
    This is a documentation test - actual vulnerability scanning should be done with tools like safety
    """
    import jwt

    # Flask 2.2.3 and earlier have known issues - we should be on 3.x
    flask_version = get_version("flask")
    assert flask_version.startswith("3."), "Flask should be version 3.x"

    # Werkzeug 2.2.3 has CVE-2023-25577 and CVE-2023-46136
    werkzeug_version = get_version("werkzeug")
    assert werkzeug_version.startswith("3."), "Werkzeug should be version 3.x"

    # PyJWT 2.8.0 and earlier have potential validation bypass issues
    version_parts = jwt.__version__.split(".")
    major = int(version_parts[0])
    minor = int(version_parts[1])
    assert major >= 2 and minor >= 10, "PyJWT should be 2.10.x or higher"
