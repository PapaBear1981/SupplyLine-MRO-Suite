"""Unit tests that exercise custody rule edge cases."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from custody import User
from custody.models import Role
from custody.rules import (
    AlreadyCheckedOutError,
    CalibrationExpiredError,
    NotCheckedOutError,
    PermissionDeniedError,
    checkout_tool,
    return_tool,
)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("role", "expected"),
    [
        (Role.ADMIN, True),
        (Role.TECHNICIAN, True),
        (Role.VIEWER, False),
        (Role.AUDITOR, False),
    ],
)
def test_role_based_checkout_permission(tool_factory, role, expected):
    tool = tool_factory(datetime.now(UTC) + timedelta(days=2))
    user = User(user_id="role-tester", role=role)
    if expected:
        checkout_tool(tool, user, at=datetime.now(UTC))
        assert tool.holder == user.user_id
    else:
        with pytest.raises(PermissionDeniedError):
            checkout_tool(tool, user, at=datetime.now(UTC))


@pytest.mark.unit
def test_cannot_checkout_when_already_checked_out(tool_factory, seeded_users):
    tool = tool_factory(datetime.now(UTC) + timedelta(days=2))
    checkout_tool(tool, seeded_users["tech"], at=datetime.now(UTC))
    with pytest.raises(AlreadyCheckedOutError):
        checkout_tool(tool, seeded_users["admin"], at=datetime.now(UTC))


@pytest.mark.unit
@pytest.mark.parametrize("hours_until_due", [0, -1, -24])
def test_calibration_blocks_checkout(tool_factory, seeded_users, hours_until_due):
    due = datetime.now(UTC) + timedelta(hours=hours_until_due)
    tool = tool_factory(due)
    with pytest.raises(CalibrationExpiredError):
        checkout_tool(tool, seeded_users["tech"], at=due)


@pytest.mark.unit
@pytest.mark.parametrize("timezone_offset", [timedelta(hours=h) for h in (-8, 0, 2, 9)])
def test_return_records_timestamp_order(tool_factory, seeded_users, timezone_offset):
    now = datetime.now(UTC)
    tool = tool_factory(now + timedelta(days=1))
    checkout_tool(tool, seeded_users["tech"], at=now + timezone_offset)
    event = return_tool(tool, seeded_users["tech"], at=now + timezone_offset + timedelta(hours=1))
    assert event.timestamp > tool.history[0].timestamp


@pytest.mark.unit
@pytest.mark.parametrize("overlap", [timedelta(minutes=0), timedelta(minutes=5)])
def test_overlapping_checkouts_blocked(tool_factory, seeded_users, overlap):
    base_time = datetime(2024, 3, 10, 1, 0, tzinfo=UTC)
    tool = tool_factory(base_time + timedelta(days=1))
    checkout_tool(tool, seeded_users["tech"], at=base_time)
    with pytest.raises(AlreadyCheckedOutError):
        checkout_tool(tool, seeded_users["admin"], at=base_time + overlap)


@pytest.mark.unit
def test_return_requires_active_checkout(tool_factory, seeded_users):
    tool = tool_factory(datetime.now(UTC) + timedelta(days=1))
    with pytest.raises(NotCheckedOutError):
        return_tool(tool, seeded_users["tech"], at=datetime.now(UTC))
