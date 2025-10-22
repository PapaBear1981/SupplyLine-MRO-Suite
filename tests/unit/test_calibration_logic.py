"""Unit tests for calibration rules and time handling."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from freezegun import freeze_time

from custody import Tool
from custody.calibration import is_calibration_valid, next_calibration_window


@pytest.mark.unit
@pytest.mark.parametrize(
    "now_offset,expected",
    [(-2, False), (-1, False), (0, False), (1, True), (24, True)],
)
def test_calibration_validity_relative_to_now(now_offset, expected):
    base = datetime(2024, 1, 1, tzinfo=UTC)
    due = base + timedelta(hours=now_offset)
    tool = Tool(tool_id="TL-200", calibration_due=due)
    with freeze_time(base):
        assert is_calibration_valid(tool) is expected


@pytest.mark.unit
@pytest.mark.parametrize("grace", [0, 7, 30])
def test_next_calibration_window(tool_factory, grace):
    due = datetime(2024, 6, 1, tzinfo=UTC)
    tool = tool_factory(due)
    start, end = next_calibration_window(tool, grace_period_days=grace)
    assert start == due - timedelta(days=grace)
    assert end == due


@pytest.mark.unit
def test_calibration_ignored_when_not_required(tool_factory):
    due = datetime(2020, 1, 1, tzinfo=UTC)
    tool = tool_factory(due, calibration_required=False)
    assert is_calibration_valid(tool) is True
