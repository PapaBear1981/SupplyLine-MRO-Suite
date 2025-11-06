"""Add department management and advanced user permissions"""
from __future__ import annotations

import os
import sqlite3
import sys
from typing import Iterable, Tuple

# Permissions to ensure exist (name, description, category)
NEW_PERMISSIONS: Tuple[Tuple[str, str, str], ...] = (
    (
        "department.create",
        "Create new departments",
        "Department Management",
    ),
    (
        "department.update",
        "Update department details",
        "Department Management",
    ),
    (
        "department.delete",
        "Deactivate departments",
        "Department Management",
    ),
    (
        "department.hard_delete",
        "Permanently delete departments",
        "Department Management",
    ),
    (
        "user.manage",
        "Manage advanced user account settings",
        "User Management",
    ),
)


def _resolve_database_path() -> str:
    """Resolve the SQLite database path from DATABASE_URL or defaults."""

    database_url = os.environ.get("DATABASE_URL", "sqlite:///database/tools.db")

    if database_url.startswith("sqlite:///"):
        db_path = database_url.replace("sqlite:///", "")
        if not os.path.isabs(db_path):
            repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(repo_root, db_path)
        return db_path

    # Fallback to default relative path inside repository
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(repo_root, "database", "tools.db")


def _ensure_permissions(cursor: sqlite3.Cursor, permissions: Iterable[Tuple[str, str, str]]) -> dict[str, int]:
    """Create permissions if they do not exist and return mapping name->id."""

    name_to_id: dict[str, int] = {}
    for name, description, category in permissions:
        cursor.execute("SELECT id FROM permissions WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            name_to_id[name] = row[0]
            continue

        cursor.execute(
            "INSERT INTO permissions (name, description, category) VALUES (?, ?, ?)",
            (name, description, category),
        )
        name_to_id[name] = cursor.lastrowid
    return name_to_id


def _assign_to_admin(cursor: sqlite3.Cursor, permission_ids: Iterable[int]) -> None:
    """Ensure Administrator role has each permission id."""

    cursor.execute("SELECT id FROM roles WHERE name = ?", ("Administrator",))
    row = cursor.fetchone()
    if not row:
        return

    admin_role_id = row[0]
    for permission_id in permission_ids:
        cursor.execute(
            "SELECT 1 FROM role_permissions WHERE role_id = ? AND permission_id = ?",
            (admin_role_id, permission_id),
        )
        if cursor.fetchone():
            continue
        cursor.execute(
            "INSERT INTO role_permissions (role_id, permission_id) VALUES (?, ?)",
            (admin_role_id, permission_id),
        )


def run_migration() -> None:
    """Run the migration ensuring new permissions are present."""

    db_path = _resolve_database_path()
    print(f"Using database at: {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        permission_map = _ensure_permissions(cursor, NEW_PERMISSIONS)
        _assign_to_admin(cursor, permission_map.values())

        conn.commit()

        print(f"Ensured {len(permission_map)} permissions (created or existing)")
        print("Administrator role updated with new department permissions")
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        run_migration()
        sys.exit(0)
    except Exception as exc:  # pragma: no cover - safety logging for manual runs
        print(f"Migration failed: {exc!s}")
        sys.exit(1)

