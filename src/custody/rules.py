"""Custody rules for check-in / check-out flows."""

from __future__ import annotations

from datetime import UTC, datetime

from .calibration import is_calibration_valid
from .models import CheckoutEvent, Role, Tool, User


class CustodyError(RuntimeError):
    """Base exception for custody rule violations."""


class AlreadyCheckedOutError(CustodyError):
    """Raised when a tool is already checked out to another user."""


class NotCheckedOutError(CustodyError):
    """Raised when attempting to return a tool that is not checked out."""


class CalibrationExpiredError(CustodyError):
    """Raised when calibration is expired but check-out is attempted."""


class PermissionDeniedError(CustodyError):
    """Raised when a user role does not allow the requested operation."""


def checkout_tool(
    tool: Tool,
    user: User,
    *,
    at: datetime | None = None,
    require_calibration_valid: bool = True,
) -> CheckoutEvent:
    """Apply the checkout mutation and return the generated event."""

    moment = at or datetime.now(UTC)
    if not user.can_checkout():
        raise PermissionDeniedError(f"User {user.user_id} cannot checkout tools")
    if tool.is_checked_out():
        raise AlreadyCheckedOutError(f"Tool {tool.tool_id} already checked out")
    if require_calibration_valid and not is_calibration_valid(tool, moment):
        raise CalibrationExpiredError(f"Tool {tool.tool_id} calibration expired")

    tool.holder = user.user_id
    tool.last_checkout = moment
    event = CheckoutEvent(type="checkout", user_id=user.user_id, timestamp=moment)
    tool.history.append(event)
    return event


def return_tool(tool: Tool, user: User, *, at: datetime | None = None) -> CheckoutEvent:
    """Return a tool to inventory, enforcing append-only history."""

    moment = at or datetime.now(UTC)
    if not tool.is_checked_out():
        raise NotCheckedOutError(f"Tool {tool.tool_id} is not checked out")
    if tool.holder != user.user_id and user.role != Role.ADMIN:
        raise PermissionDeniedError("Only the holder or an admin can return a tool")

    tool.holder = None
    event = CheckoutEvent(type="return", user_id=user.user_id, timestamp=moment)
    tool.history.append(event)
    return event
