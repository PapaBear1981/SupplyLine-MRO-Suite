"""Property-based tests for custody invariants."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, rule

from custody import Tool, User
from custody.models import Role
from custody.rules import (
    AlreadyCheckedOutError,
    CalibrationExpiredError,
    CustodyError,
    NotCheckedOutError,
    PermissionDeniedError,
    checkout_tool,
    return_tool,
)


class CustodyStateMachine(RuleBasedStateMachine):
    def __init__(self) -> None:
        super().__init__()
        base_time = datetime(2024, 1, 1, tzinfo=UTC)
        self.tool = Tool(tool_id="TL-STATE", calibration_due=base_time + timedelta(days=30))
        self.users = {
            "admin": User(user_id="u-admin", role=Role.ADMIN),
            "tech": User(user_id="u-tech", role=Role.TECHNICIAN),
            "viewer": User(user_id="u-view", role=Role.VIEWER),
        }
        self.require_valid = True
        self.now = base_time
        self.last_error: CustodyError | None = None

    @initialize()
    def reset(self) -> None:
        self.tool.holder = None
        self.tool.history.clear()
        self.tool.calibration_due = self.now + timedelta(days=30)
        self.require_valid = True
        self.last_error = None

    @rule(delta=st.timedeltas(min_value=timedelta(minutes=-5), max_value=timedelta(days=2)))
    def advance_time(self, delta: timedelta) -> None:
        self.now = self.now + delta

    @rule(require_valid=st.booleans())
    def set_policy(self, require_valid: bool) -> None:
        self.require_valid = require_valid

    @rule(expired=st.booleans())
    def set_calibration_state(self, expired: bool) -> None:
        if expired:
            self.tool.calibration_due = self.now - timedelta(minutes=1)
        else:
            self.tool.calibration_due = self.now + timedelta(days=3)

    @rule(user=st.sampled_from(["admin", "tech", "viewer"]))
    def checkout(self, user: str) -> None:
        actor = self.users[user]
        try:
            checkout_tool(self.tool, actor, at=self.now, require_calibration_valid=self.require_valid)
            self.last_error = None
        except CalibrationExpiredError:
            assert self.require_valid and self.tool.calibration_due <= self.now
            self.last_error = CalibrationExpiredError("expired")
        except PermissionDeniedError:
            assert not actor.can_checkout()
            self.last_error = PermissionDeniedError("denied")
        except AlreadyCheckedOutError:
            assert self.tool.holder is not None
            self.last_error = AlreadyCheckedOutError("occupied")

    @rule(user=st.sampled_from(["admin", "tech", "viewer"]))
    def return_action(self, user: str) -> None:
        actor = self.users[user]
        try:
            return_tool(self.tool, actor, at=self.now)
            self.last_error = None
        except NotCheckedOutError:
            assert not self.tool.is_checked_out()
            self.last_error = NotCheckedOutError("empty")
        except PermissionDeniedError:
            assert self.tool.is_checked_out() and actor.role not in {Role.ADMIN} and actor.user_id != self.tool.holder
            self.last_error = PermissionDeniedError("return-denied")

    @invariant()
    def at_most_one_holder(self) -> None:
        holders = {event.user_id for event in self.tool.history if event.type == "checkout"}
        active_holders = [holder for holder in holders if holder == self.tool.holder]
        assert len(active_holders) <= 1

    @invariant()
    def returns_require_checkout(self) -> None:
        returns = sum(1 for event in self.tool.history if event.type == "return")
        checkouts = sum(1 for event in self.tool.history if event.type == "checkout")
        assert returns <= checkouts

    @invariant()
    def expired_calibration_blocks_checkout(self) -> None:
        if self.require_valid and self.tool.calibration_due <= self.now:
            assert self.tool.holder is None


CustodyStateMachine.TestCase.settings = settings(max_examples=50, stateful_step_count=25)


@pytest.mark.property
def test_custody_state_machine():
    CustodyStateMachine.TestCase().runTest()


@pytest.mark.property
@given(
    st.lists(
        st.sampled_from(["checkout", "return"]),
        min_size=1,
        max_size=10,
    )
)
def test_sequence_invariants(sequence):
    tool = Tool(tool_id="TL-PROP", calibration_due=datetime(2024, 1, 1, tzinfo=UTC) + timedelta(days=10))
    tech = User(user_id="u-tech", role=Role.TECHNICIAN)
    for action in sequence:
        if action == "checkout":
            if tool.is_checked_out():
                with pytest.raises(AlreadyCheckedOutError):
                    checkout_tool(tool, tech, at=datetime.now(UTC))
            else:
                checkout_tool(tool, tech, at=datetime.now(UTC))
        else:
            if tool.is_checked_out():
                return_tool(tool, tech, at=datetime.now(UTC))
            else:
                with pytest.raises(NotCheckedOutError):
                    return_tool(tool, tech, at=datetime.now(UTC))

    assert sum(1 for event in tool.history if event.type == "checkout") >= sum(
        1 for event in tool.history if event.type == "return"
    )
