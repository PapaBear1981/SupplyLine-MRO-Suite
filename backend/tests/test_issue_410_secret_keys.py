"""
Test for Issue #410: Hardcoded Default Secret Keys
Ensures that the application requires SECRET_KEY and JWT_SECRET_KEY to be set
"""

import os
import sys

import pytest


# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_secret_key_required_in_production():
    """Test that SECRET_KEY is required when not in testing mode"""
    from flask import Flask

    from config import Config

    # Save original environment
    original_secret = os.environ.get("SECRET_KEY")
    original_jwt_secret = os.environ.get("JWT_SECRET_KEY")
    original_flask_env = os.environ.get("FLASK_ENV")
    original_ci = os.environ.get("CI")
    original_github_actions = os.environ.get("GITHUB_ACTIONS")

    try:
        # Remove secrets and set production mode
        if "SECRET_KEY" in os.environ:
            del os.environ["SECRET_KEY"]
        if "JWT_SECRET_KEY" in os.environ:
            del os.environ["JWT_SECRET_KEY"]
        # Remove CI flags to test actual production behavior
        if "CI" in os.environ:
            del os.environ["CI"]
        if "GITHUB_ACTIONS" in os.environ:
            del os.environ["GITHUB_ACTIONS"]
        os.environ["FLASK_ENV"] = "production"

        # Test Config.validate_security_config directly with missing keys
        with pytest.raises(RuntimeError, match="SECRET_KEY must be set for production environment"):
            test_config = {
                "TESTING": False,
                "SECRET_KEY": None,
                "JWT_SECRET_KEY": None,
                "FLASK_ENV": "production",
                "ENVIRONMENT": "production"
            }
            Config.validate_security_config(test_config)

    finally:
        # Restore original environment
        if original_secret:
            os.environ["SECRET_KEY"] = original_secret
        elif "SECRET_KEY" in os.environ:
            del os.environ["SECRET_KEY"]

        if original_jwt_secret:
            os.environ["JWT_SECRET_KEY"] = original_jwt_secret
        elif "JWT_SECRET_KEY" in os.environ:
            del os.environ["JWT_SECRET_KEY"]

        if original_flask_env:
            os.environ["FLASK_ENV"] = original_flask_env
        elif "FLASK_ENV" in os.environ:
            del os.environ["FLASK_ENV"]

        if original_ci:
            os.environ["CI"] = original_ci
        elif "CI" in os.environ:
            del os.environ["CI"]

        if original_github_actions:
            os.environ["GITHUB_ACTIONS"] = original_github_actions
        elif "GITHUB_ACTIONS" in os.environ:
            del os.environ["GITHUB_ACTIONS"]


def test_jwt_secret_key_required_in_production():
    """Test that JWT_SECRET_KEY is required when not in testing mode"""
    from flask import Flask

    from config import Config

    # Save original environment
    original_secret = os.environ.get("SECRET_KEY")
    original_jwt_secret = os.environ.get("JWT_SECRET_KEY")
    original_flask_env = os.environ.get("FLASK_ENV")
    original_ci = os.environ.get("CI")
    original_github_actions = os.environ.get("GITHUB_ACTIONS")

    try:
        # Set SECRET_KEY but remove JWT_SECRET_KEY
        os.environ["SECRET_KEY"] = "test-secret-for-validation"
        if "JWT_SECRET_KEY" in os.environ:
            del os.environ["JWT_SECRET_KEY"]
        # Remove CI flags to test actual production behavior
        if "CI" in os.environ:
            del os.environ["CI"]
        if "GITHUB_ACTIONS" in os.environ:
            del os.environ["GITHUB_ACTIONS"]
        os.environ["FLASK_ENV"] = "production"

        # Test Config.validate_security_config directly with missing JWT key
        with pytest.raises(RuntimeError, match="JWT_SECRET_KEY must be set for production environment"):
            test_config = {
                "TESTING": False,
                "SECRET_KEY": "test-secret-for-validation",
                "JWT_SECRET_KEY": None,
                "FLASK_ENV": "production",
                "ENVIRONMENT": "production"
            }
            Config.validate_security_config(test_config)

    finally:
        # Restore original environment
        if original_secret:
            os.environ["SECRET_KEY"] = original_secret
        elif "SECRET_KEY" in os.environ:
            del os.environ["SECRET_KEY"]

        if original_jwt_secret:
            os.environ["JWT_SECRET_KEY"] = original_jwt_secret
        elif "JWT_SECRET_KEY" in os.environ:
            del os.environ["JWT_SECRET_KEY"]

        if original_flask_env:
            os.environ["FLASK_ENV"] = original_flask_env
        elif "FLASK_ENV" in os.environ:
            del os.environ["FLASK_ENV"]

        if original_ci:
            os.environ["CI"] = original_ci
        elif "CI" in os.environ:
            del os.environ["CI"]

        if original_github_actions:
            os.environ["GITHUB_ACTIONS"] = original_github_actions
        elif "GITHUB_ACTIONS" in os.environ:
            del os.environ["GITHUB_ACTIONS"]


def test_secret_key_required_in_staging_like_environment():
    """Ensure staging-like deployments require explicit secrets."""
    from flask import Flask

    from config import Config

    original_env = {
        "SECRET_KEY": os.environ.get("SECRET_KEY"),
        "JWT_SECRET_KEY": os.environ.get("JWT_SECRET_KEY"),
        "FLASK_ENV": os.environ.get("FLASK_ENV"),
        "ENVIRONMENT": os.environ.get("ENVIRONMENT"),
        "CI": os.environ.get("CI"),
        "GITHUB_ACTIONS": os.environ.get("GITHUB_ACTIONS"),
    }

    try:
        for key in ("SECRET_KEY", "JWT_SECRET_KEY", "CI", "GITHUB_ACTIONS"):
            if key in os.environ:
                del os.environ[key]
        os.environ["FLASK_ENV"] = "staging"
        os.environ["ENVIRONMENT"] = "staging"

        # Test Config.validate_security_config directly with missing keys
        with pytest.raises(RuntimeError, match="SECRET_KEY must be set for staging environment"):
            test_config = {
                "TESTING": False,
                "SECRET_KEY": None,
                "JWT_SECRET_KEY": None,
                "FLASK_ENV": "staging",
                "ENVIRONMENT": "staging"
            }
            Config.validate_security_config(test_config)

    finally:
        for key, value in original_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]


def test_secrets_allowed_in_testing_mode():
    """Test that secrets can be set via config in testing mode"""
    from flask import Flask

    from config import Config

    # Save original environment
    original_flask_env = os.environ.get("FLASK_ENV")
    original_secret = os.environ.get("SECRET_KEY")
    original_jwt_secret = os.environ.get("JWT_SECRET_KEY")

    try:
        # Set testing mode
        os.environ["FLASK_ENV"] = "testing"

        # Remove secrets from environment
        if "SECRET_KEY" in os.environ:
            del os.environ["SECRET_KEY"]
        if "JWT_SECRET_KEY" in os.environ:
            del os.environ["JWT_SECRET_KEY"]

        # This should NOT raise an error in testing mode
        app = Flask(__name__)
        app.config.from_object(Config)
        app.config["TESTING"] = True

        # Set secrets via config (allowed in testing mode)
        app.config["SECRET_KEY"] = "test-secret-key"
        app.config["JWT_SECRET_KEY"] = "test-jwt-secret-key"

        # Config.validate_security_config should not raise an error
        Config.validate_security_config(app.config)

        # Verify secrets are set
        assert app.config["SECRET_KEY"] == "test-secret-key"
        assert app.config["JWT_SECRET_KEY"] == "test-jwt-secret-key"

    finally:
        # Restore original environment
        if original_flask_env:
            os.environ["FLASK_ENV"] = original_flask_env
        elif "FLASK_ENV" in os.environ:
            del os.environ["FLASK_ENV"]

        if original_secret:
            os.environ["SECRET_KEY"] = original_secret
        elif "SECRET_KEY" in os.environ:
            del os.environ["SECRET_KEY"]

        if original_jwt_secret:
            os.environ["JWT_SECRET_KEY"] = original_jwt_secret
        elif "JWT_SECRET_KEY" in os.environ:
            del os.environ["JWT_SECRET_KEY"]


def test_ephemeral_secrets_generated_in_ci_environment():
    """Ensure CI environments receive generated secrets instead of raising errors."""
    from flask import Flask

    from config import Config

    original_env = {
        "SECRET_KEY": os.environ.get("SECRET_KEY"),
        "JWT_SECRET_KEY": os.environ.get("JWT_SECRET_KEY"),
        "FLASK_ENV": os.environ.get("FLASK_ENV"),
        "CI": os.environ.get("CI"),
        "GITHUB_ACTIONS": os.environ.get("GITHUB_ACTIONS"),
    }

    try:
        for key in ("SECRET_KEY", "JWT_SECRET_KEY", "GITHUB_ACTIONS"):
            if key in os.environ:
                del os.environ[key]
        os.environ["FLASK_ENV"] = "production"
        os.environ["CI"] = "true"

        app = Flask(__name__)
        app.config["TESTING"] = False
        app.config["SECRET_KEY"] = None
        app.config["JWT_SECRET_KEY"] = None

        Config.validate_security_config(app.config)

        assert app.config["SECRET_KEY"], "SECRET_KEY should be generated in CI"
        assert app.config["JWT_SECRET_KEY"], "JWT_SECRET_KEY should be generated in CI"
        assert app.config["SECRET_KEY"] != app.config["JWT_SECRET_KEY"], "Generated secrets should differ"

    finally:
        for key, value in original_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]


def test_secrets_work_when_provided():
    """Test that application works correctly when secrets are provided"""
    # Save original environment
    original_secret = os.environ.get("SECRET_KEY")
    original_jwt_secret = os.environ.get("JWT_SECRET_KEY")
    original_flask_env = os.environ.get("FLASK_ENV")

    try:
        # Set valid secrets
        os.environ["SECRET_KEY"] = "test-secret-key-for-validation"
        os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-for-validation"
        os.environ["FLASK_ENV"] = "production"

        # Reload config and app modules to pick up new environment variables
        import importlib

        import app
        import config
        importlib.reload(config)
        importlib.reload(app)

        # This should work fine
        app = app.create_app()

        assert app.config["SECRET_KEY"] == "test-secret-key-for-validation"
        assert app.config["JWT_SECRET_KEY"] == "test-jwt-secret-key-for-validation"

    finally:
        # Restore original environment
        if original_secret:
            os.environ["SECRET_KEY"] = original_secret
        elif "SECRET_KEY" in os.environ:
            del os.environ["SECRET_KEY"]

        if original_jwt_secret:
            os.environ["JWT_SECRET_KEY"] = original_jwt_secret
        elif "JWT_SECRET_KEY" in os.environ:
            del os.environ["JWT_SECRET_KEY"]

        if original_flask_env:
            os.environ["FLASK_ENV"] = original_flask_env
        elif "FLASK_ENV" in os.environ:
            del os.environ["FLASK_ENV"]

        # Reload config module to restore normal state
        if "config" in sys.modules:
            del sys.modules["config"]
