"""Tests covering backup and restore flows."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import select

from custody.db import audit_table, backup_database, restore_database, setup_schema, tool_table
from custody.db import create_sqlite_engine


@pytest.mark.db
def test_backup_and_restore_round_trip(tmp_backup_path, tmp_path):
    engine = create_sqlite_engine(f"sqlite+pysqlite:///{tmp_path / 'source.sqlite'}")
    setup_schema(engine)
    with engine.begin() as connection:
        connection.execute(
            tool_table.insert(),
            [
                {
                    "id": 1,
                    "tool_id": "TL-100",
                    "holder": "u-tech",
                    "calibration_due": datetime(2024, 1, 10, tzinfo=UTC),
                }
            ],
        )
        connection.execute(
            audit_table.insert(),
            [
                {
                    "id": 1,
                    "tool_id": "TL-100",
                    "action": "checkout",
                    "actor": "u-tech",
                    "timestamp": datetime(2024, 1, 1, tzinfo=UTC),
                }
            ],
        )

    backup_database(engine, destination=tmp_backup_path)

    target_engine = create_sqlite_engine(f"sqlite+pysqlite:///{tmp_path / 'restored.sqlite'}")
    setup_schema(target_engine)
    restore_database(target_engine, source=tmp_backup_path)

    with target_engine.connect() as connection:
        tools = connection.execute(select(tool_table)).all()
        audits = connection.execute(select(audit_table)).all()
    assert len(tools) == 1
    assert len(audits) == 1
    assert tools[0].tool_id == "TL-100"
    assert audits[0].action == "checkout"
