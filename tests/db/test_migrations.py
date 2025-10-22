"""Alembic smoke tests for applying and downgrading migrations."""

from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, create_engine

ALEMBIC_ROOT = Path(__file__).resolve().parent / "alembic"
ALEMBIC_INI = Path(__file__).resolve().parent / "alembic.ini"


@pytest.mark.db
def test_alembic_upgrade_and_downgrade(tmp_path):
    db_path = tmp_path / "migration.sqlite"
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("script_location", str(ALEMBIC_ROOT))
    config.set_main_option("sqlalchemy.url", f"sqlite+pysqlite:///{db_path}")

    command.upgrade(config, "head")

    engine = create_engine(f"sqlite+pysqlite:///{db_path}", future=True)
    inspector = inspect(engine)
    assert "audit_entries" in inspector.get_table_names()

    command.downgrade(config, "base")
    inspector = inspect(engine)
    assert "audit_entries" not in inspector.get_table_names()

    command.upgrade(config, "head")
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns("audit_entries")}
    assert {"id", "tool_id", "action", "actor", "timestamp", "notes"}.issubset(columns)
    engine.dispose()
