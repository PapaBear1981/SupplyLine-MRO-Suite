"""SQLite helpers that mimic backup / restore workflows for tests."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.sql import select


metadata = MetaData()
audit_table = Table(
    "audit_entries",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("tool_id", String, nullable=False),
    Column("action", String, nullable=False),
    Column("actor", String, nullable=False),
    Column("timestamp", DateTime, nullable=False),
)

tool_table = Table(
    "tools",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("tool_id", String, nullable=False, unique=True),
    Column("holder", String, nullable=True),
    Column("calibration_due", DateTime, nullable=False),
)


def setup_schema(engine: Engine) -> None:
    """Create the minimal tables used in the smoke tests."""

    metadata.create_all(engine)


def backup_database(engine: Engine, *, destination: Path) -> Path:
    """Dump simple table payloads into JSON for deterministic restore."""

    payload: dict[str, list[dict]] = {}
    with engine.begin() as connection:
        payload["tools"] = [dict(row) for row in connection.execute(select(tool_table))]
        payload["audit_entries"] = [dict(row) for row in connection.execute(select(audit_table))]
    destination.write_text(json.dumps(payload, default=str, indent=2))
    return destination


def restore_database(engine: Engine, *, source: Path) -> None:
    """Load the JSON dump created by :func:`backup_database`."""

    payload = json.loads(source.read_text())
    with engine.begin() as connection:
        connection.execute(tool_table.delete())
        connection.execute(audit_table.delete())
        if payload["tools"]:
            connection.execute(tool_table.insert(), payload["tools"])
        if payload["audit_entries"]:
            connection.execute(audit_table.insert(), payload["audit_entries"])


def create_sqlite_engine(database_url: str | None = None) -> Engine:
    """Helper used in fixtures and CLI utilities."""

    url = database_url or "sqlite+pysqlite:///:memory:"
    return create_engine(url, future=True)

__all__ = [
    "audit_table",
    "backup_database",
    "create_sqlite_engine",
    "restore_database",
    "setup_schema",
    "tool_table",
]
