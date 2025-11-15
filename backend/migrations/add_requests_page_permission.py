"""Migration script to add the Requests page permission."""

import io
import os
import secrets
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if sys.platform == "win32":  # pragma: no cover - platform specific safety
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from app import create_app  # noqa: E402
from models import Permission, Role, RolePermission, db  # noqa: E402


def _ensure_security_defaults():
    os.environ.setdefault("FLASK_ENV", "testing")
    os.environ.setdefault("SECRET_KEY", secrets.token_urlsafe(64))
    os.environ.setdefault("JWT_SECRET_KEY", secrets.token_urlsafe(64))


def run_migration():
    _ensure_security_defaults()

    app = create_app()

    with app.app_context():
        print("Starting requests page permission migration...")

        permission = Permission.query.filter_by(name="page.requests").first()
        if permission:
            print("  ℹ️  Permission 'page.requests' already exists")
        else:
            permission = Permission(
                name="page.requests",
                description="Access Requests page",
                category="Page Access",
            )
            db.session.add(permission)
            db.session.commit()
            print("  ✅ Created permission: page.requests")

        target_roles = [
            "Administrator",
            "Materials Manager",
            "Maintenance User",
            "Quality Inspector",
        ]
        assignments = 0
        for role_name in target_roles:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                print(f"  ⚠️  Role '{role_name}' not found; assign permission manually if needed")
                continue

            existing = RolePermission.query.filter_by(
                role_id=role.id,
                permission_id=permission.id,
            ).first()
            if existing:
                print(f"  ℹ️  Role '{role_name}' already has page.requests")
                continue

            db.session.add(RolePermission(role_id=role.id, permission_id=permission.id))
            assignments += 1
            print(f"  ✅ Granted page.requests to role '{role_name}'")

        if assignments:
            db.session.commit()

        print("Migration complete.")


if __name__ == "__main__":  # pragma: no cover - manual execution entrypoint
    run_migration()
