"""Utilities for securing the password reset confirmation workflow."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading


@dataclass
class ResetAttemptState:
    """State information for password reset attempts."""

    failures: int = 0
    lock_until: datetime | None = None


class PasswordResetSecurityTracker:
    """Track password reset confirmation attempts per account.

    This tracker provides account-level controls for password reset
    confirmations, including exponential backoff after each failed attempt
    and the ability to determine when additional attempts should be blocked.
    """

    MAX_FAILURES = 3
    BASE_DELAY_SECONDS = 5
    MAX_DELAY_SECONDS = 300  # Cap exponential backoff at 5 minutes

    def __init__(self) -> None:
        self._attempts: defaultdict[str, ResetAttemptState] = defaultdict(ResetAttemptState)
        self._lock = threading.Lock()

    def _get_state(self, employee_number: str) -> ResetAttemptState:
        return self._attempts[employee_number]

    def is_locked(self, employee_number: str) -> tuple[bool, int]:
        """Return whether the employee is locked out and seconds remaining."""

        with self._lock:
            state = self._attempts.get(employee_number)
            if not state or not state.lock_until:
                return False, 0

            now = datetime.utcnow()
            if state.lock_until > now:
                retry_after = int((state.lock_until - now).total_seconds())
                return True, max(retry_after, 1)

            # Lock expired, clear it but retain failure count
            state.lock_until = None
            return False, 0

    def record_failure(self, employee_number: str) -> tuple[int, int]:
        """Record a failed confirmation attempt.

        Returns a tuple containing the remaining attempts before the token
        should be invalidated and the calculated retry-after seconds due to
        exponential backoff.
        """

        with self._lock:
            state = self._get_state(employee_number)
            state.failures += 1

            delay_seconds = min(
                self.MAX_DELAY_SECONDS,
                self.BASE_DELAY_SECONDS * (2 ** (state.failures - 1)),
            )
            state.lock_until = datetime.utcnow() + timedelta(seconds=delay_seconds)

            remaining_attempts = max(self.MAX_FAILURES - state.failures, 0)
            return remaining_attempts, delay_seconds

    def reset(self, employee_number: str) -> None:
        """Clear attempt tracking for an employee."""

        with self._lock:
            self._attempts.pop(employee_number, None)

    def reset_all(self) -> None:
        """Clear all tracked attempts. Primarily used in tests."""

        with self._lock:
            self._attempts.clear()

    def force_unlock(self, employee_number: str) -> None:
        """Remove any active lock while retaining failure count (testing helper)."""

        with self._lock:
            state = self._attempts.get(employee_number)
            if state:
                state.lock_until = None

    def should_invalidate_token(self, employee_number: str) -> bool:
        """Return whether the max failures threshold has been reached."""

        with self._lock:
            state = self._attempts.get(employee_number)
            if not state:
                return False
            return state.failures >= self.MAX_FAILURES


# Global tracker instance used by the application
password_reset_security_tracker = PasswordResetSecurityTracker()


def get_password_reset_tracker() -> PasswordResetSecurityTracker:
    """Expose the global password reset tracker for use in other modules."""

    return password_reset_security_tracker

