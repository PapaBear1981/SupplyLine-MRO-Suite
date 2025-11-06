"""Utilities for managing system-level security settings."""


from flask import current_app

from models import SystemSetting, db


SESSION_TIMEOUT_KEY = "session_inactivity_timeout_minutes"
DEFAULT_SESSION_TIMEOUT_MINUTES = 30
MIN_SESSION_TIMEOUT_MINUTES = 5
MAX_SESSION_TIMEOUT_MINUTES = 240


def _coerce_timeout_value(raw_value: int | str | None, default: int) -> int:
    """Convert the stored timeout value to a safe integer within bounds."""
    try:
        minutes = int(raw_value)
    except (TypeError, ValueError):
        return default

    if minutes < MIN_SESSION_TIMEOUT_MINUTES or minutes > MAX_SESSION_TIMEOUT_MINUTES:
        return default

    return minutes


def get_session_timeout_value(default: int | None = None) -> int:
    """Return the configured inactivity timeout, falling back to defaults."""
    if default is None:
        default = int(
            current_app.config.get(
                "SESSION_INACTIVITY_TIMEOUT_MINUTES_DEFAULT",
                current_app.config.get(
                    "SESSION_INACTIVITY_TIMEOUT_MINUTES",
                    DEFAULT_SESSION_TIMEOUT_MINUTES,
                ),
            )
        )

    setting = SystemSetting.query.filter_by(key=SESSION_TIMEOUT_KEY).first()
    if not setting:
        return _coerce_timeout_value(default, DEFAULT_SESSION_TIMEOUT_MINUTES)

    return _coerce_timeout_value(setting.value, default)


def set_session_timeout_value(minutes: int, user_id: int | None = None, commit: bool = True) -> SystemSetting:
    """Persist the inactivity timeout and optionally commit the change."""
    if minutes < MIN_SESSION_TIMEOUT_MINUTES or minutes > MAX_SESSION_TIMEOUT_MINUTES:
        raise ValueError(
            f"Timeout must be between {MIN_SESSION_TIMEOUT_MINUTES} and {MAX_SESSION_TIMEOUT_MINUTES} minutes",
        )

    setting = SystemSetting.query.filter_by(key=SESSION_TIMEOUT_KEY).first()
    if not setting:
        setting = SystemSetting(
            key=SESSION_TIMEOUT_KEY,
            value=str(minutes),
            category="security",
            description="Session inactivity timeout in minutes",
            is_sensitive=False,
        )
        db.session.add(setting)
    else:
        setting.value = str(minutes)

    setting.updated_by_id = user_id

    if commit:
        db.session.commit()

    return setting


def load_security_settings(app) -> int:
    """Load persisted security settings into the Flask app config."""
    with app.app_context():
        baseline_default = int(
            app.config.get(
                "SESSION_INACTIVITY_TIMEOUT_MINUTES",
                DEFAULT_SESSION_TIMEOUT_MINUTES,
            )
        )
        app.config.setdefault(
            "SESSION_INACTIVITY_TIMEOUT_MINUTES_DEFAULT",
            baseline_default,
        )

        minutes = get_session_timeout_value(default=baseline_default)
        app.config["SESSION_INACTIVITY_TIMEOUT_MINUTES"] = minutes
        return minutes
