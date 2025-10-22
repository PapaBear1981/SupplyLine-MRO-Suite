"""Calibration helpers used by unit and service tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from .models import Tool


def is_calibration_valid(tool: Tool, when: datetime | None = None) -> bool:
    """Return ``True`` when the tool is within its calibration window."""

    moment = when or datetime.now(UTC)
    if not tool.calibration_required:
        return True
    return tool.calibration_due > moment


def next_calibration_window(tool: Tool, *, grace_period_days: int = 0) -> tuple[datetime, datetime]:
    """Compute the previous/next calibration boundary for reporting."""

    window_end = tool.calibration_due
    window_start = window_end - timedelta(days=grace_period_days)
    return window_start, window_end
