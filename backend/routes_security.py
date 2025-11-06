from flask import current_app, jsonify, request

from auth import jwt_required, permission_required
from models import AuditLog, SystemSetting, User, db
from utils.system_settings import (
    DEFAULT_SESSION_TIMEOUT_MINUTES,
    MAX_SESSION_TIMEOUT_MINUTES,
    MIN_SESSION_TIMEOUT_MINUTES,
    SESSION_TIMEOUT_KEY,
    get_session_timeout_value,
    set_session_timeout_value,
)


def _serialize_security_settings(timeout_minutes: int, setting: SystemSetting | None):
    updated_by = None
    if setting and setting.updated_by:
        updated_by = {
            "id": setting.updated_by.id,
            "name": setting.updated_by.name,
            "employee_number": setting.updated_by.employee_number,
        }

    return {
        "session_timeout_minutes": timeout_minutes,
        "default_timeout_minutes": current_app.config.get(
            "SESSION_INACTIVITY_TIMEOUT_MINUTES_DEFAULT",
            DEFAULT_SESSION_TIMEOUT_MINUTES,
        ),
        "min_timeout_minutes": MIN_SESSION_TIMEOUT_MINUTES,
        "max_timeout_minutes": MAX_SESSION_TIMEOUT_MINUTES,
        "source": "database" if setting else "config",
        "updated_at": setting.updated_at.isoformat() if setting and setting.updated_at else None,
        "updated_by": updated_by,
    }


def register_security_routes(app):
    @app.route("/api/security/settings", methods=["GET"])
    @jwt_required
    def get_security_settings():
        timeout_minutes = get_session_timeout_value()
        setting = SystemSetting.query.filter_by(key=SESSION_TIMEOUT_KEY).first()
        return jsonify(_serialize_security_settings(timeout_minutes, setting))

    @app.route("/api/security/settings", methods=["PUT"])
    @permission_required("system.settings")
    def update_security_settings():
        payload = request.get_json() or {}
        timeout_minutes = payload.get("session_timeout_minutes")

        if timeout_minutes is None:
            return jsonify({"error": "session_timeout_minutes is required"}), 400

        try:
            timeout_minutes = int(timeout_minutes)
        except (TypeError, ValueError):
            return jsonify({"error": "session_timeout_minutes must be an integer"}), 400

        if timeout_minutes < MIN_SESSION_TIMEOUT_MINUTES or timeout_minutes > MAX_SESSION_TIMEOUT_MINUTES:
            return jsonify({
                "error": (
                    f"session_timeout_minutes must be between {MIN_SESSION_TIMEOUT_MINUTES} and "
                    f"{MAX_SESSION_TIMEOUT_MINUTES} minutes"
                )
            }), 400

        user_id = request.current_user["user_id"]
        setting = set_session_timeout_value(timeout_minutes, user_id=user_id, commit=False)

        audit_entry = AuditLog(
            action_type="update_security_setting",
            action_details=(
                f"User {user_id} updated session inactivity timeout to {timeout_minutes} minutes"
            ),
        )
        db.session.add(audit_entry)
        db.session.commit()
        db.session.refresh(setting)

        # Attach relationship info manually when refreshed in a new session context
        if not setting.updated_by and setting.updated_by_id:
            setting.updated_by = db.session.get(User, setting.updated_by_id)

        return jsonify(_serialize_security_settings(timeout_minutes, setting)), 200
