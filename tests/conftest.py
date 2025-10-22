"""Shared pytest fixtures for the quality gates."""

from __future__ import annotations

import os
import sys
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Callable, Dict

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from freezegun import freeze_time
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from custody import AuditEntry, AuditLog, Role, Tool, User
from custody.db import setup_schema

DEFAULT_API_BASE_URL = "https://api.example.com"


class APIClient:
    """Very small HTTP client that enforces auth headers in tests."""

    def __init__(self, base_url: str, token: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        if token:
            self._session.headers.update({"Authorization": f"Bearer {token}"})

    def request(self, method: str, path: str, **kwargs):  # pragma: no cover - thin wrapper
        url = f"{self.base_url}{path}"
        return self._session.request(method, url, **kwargs)

    def close(self) -> None:
        self._session.close()


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return os.getenv("API_BASE_URL", DEFAULT_API_BASE_URL)


@pytest.fixture(scope="session")
def api_token() -> str:
    return os.getenv("API_TOKEN", "test-token")


@pytest.fixture
def api_client(api_base_url: str, api_token: str) -> Iterator[APIClient]:
    client = APIClient(api_base_url, api_token)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture(scope="session")
def database_url(tmp_path_factory: pytest.TempPathFactory) -> str:
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    # TODO: swap this SQLite fallback with a Postgres Testcontainers setup when available.
    db_dir = tmp_path_factory.mktemp("db")
    return f"sqlite+pysqlite:///{db_dir / 'quality.sqlite'}"


@pytest.fixture(scope="session")
def engine(database_url: str) -> Iterator[Engine]:
    engine = create_engine(database_url, future=True)
    setup_schema(engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture()
def frozen_time() -> Iterator[Callable[[datetime | str], None]]:
    """Freeze time for deterministic assertions."""

    with freeze_time("2024-01-01T12:00:00Z") as freezer:
        yield freezer


@pytest.fixture()
def seeded_users() -> Dict[str, User]:
    return {
        "admin": User(user_id="u-admin", role=Role.ADMIN),
        "tech": User(user_id="u-tech", role=Role.TECHNICIAN),
        "viewer": User(user_id="u-view", role=Role.VIEWER),
        "auditor": User(user_id="u-audit", role=Role.AUDITOR),
    }


@pytest.fixture()
def tool_factory() -> Callable[[datetime, bool], Tool]:
    def factory(calibration_due: datetime, calibration_required: bool = True) -> Tool:
        return Tool(tool_id="TL-100", calibration_due=calibration_due, calibration_required=calibration_required)

    return factory


@pytest.fixture()
def sample_audit_log() -> AuditLog:
    now = datetime.now(UTC)
    log = AuditLog()
    log.append(
        AuditEntry(id=1, tool_id="TL-100", action="checkout", actor="u-tech", timestamp=now, payload={"work_order": "WO-1"})
    )
    return log


@pytest.fixture(scope="session")
def timezone_offsets() -> list[str]:
    return ["UTC", "US/Pacific", "Europe/Berlin", "Asia/Tokyo"]


@pytest.fixture()
def dst_transition_window() -> tuple[datetime, datetime]:
    start = datetime(2024, 3, 10, 1, 30, tzinfo=UTC)
    end = start + timedelta(hours=2)
    return start, end


@pytest.fixture()
def tmp_backup_path(tmp_path: Path) -> Path:
    return tmp_path / "backup.json"
