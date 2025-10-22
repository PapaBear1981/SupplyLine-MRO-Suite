"""Domain models used in the quality gate scaffolding.

These dataclasses are intentionally tiny so tests can import them without
pulling the full production ORM models. They mimic the shape of the real
objects closely enough for the quality layers defined in this kata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class Role(str, Enum):
    """Minimal set of roles for the role-based tests."""

    ADMIN = "admin"
    TECHNICIAN = "technician"
    VIEWER = "viewer"
    AUDITOR = "auditor"


@dataclass
class User:
    """Simplified user model with role metadata."""

    user_id: str
    role: Role

    def can_checkout(self) -> bool:
        return self.role in {Role.ADMIN, Role.TECHNICIAN}

    def can_view_exports(self) -> bool:
        return self.role in {Role.ADMIN, Role.AUDITOR}


@dataclass
class Tool:
    """Representation of a tool's custody state."""

    tool_id: str
    calibration_due: datetime
    holder: Optional[str] = None
    last_checkout: Optional[datetime] = None
    calibration_required: bool = True
    history: list["CheckoutEvent"] = field(default_factory=list)

    def is_checked_out(self) -> bool:
        return self.holder is not None


@dataclass
class CheckoutEvent:
    """Simple event representation for property tests."""

    type: str  # "checkout" or "return"
    user_id: str
    timestamp: datetime


@dataclass
class AuditEntry:
    """Audit entry representation used by the append-only log."""

    id: int
    tool_id: str
    action: str
    actor: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    previous_hash: Optional[str] = None
    entry_hash: Optional[str] = None
    payload: dict = field(default_factory=dict)
