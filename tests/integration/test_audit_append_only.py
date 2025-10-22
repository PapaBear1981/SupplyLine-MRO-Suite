"""Integration tests ensuring audit logs are append-only."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from custody import AuditEntry


@pytest.mark.integration
def test_append_only_enforced(sample_audit_log):
    log = sample_audit_log
    next_entry = AuditEntry(
        id=2,
        tool_id="TL-100",
        action="return",
        actor="u-tech",
        timestamp=datetime.now(UTC) + timedelta(hours=1),
        payload={"condition": "good"},
    )
    log.append(next_entry)
    assert log.verify() is True

    with pytest.raises(ValueError):
        log.append(
            AuditEntry(
                id=1,
                tool_id="TL-100",
                action="tamper",
                actor="intruder",
                timestamp=datetime.now(UTC),
            )
        )


@pytest.mark.integration
def test_hash_chain_detects_mutation(sample_audit_log):
    log = sample_audit_log
    log.append(
        AuditEntry(
            id=2,
            tool_id="TL-100",
            action="return",
            actor="u-tech",
            timestamp=datetime.now(UTC) + timedelta(hours=2),
            payload={"condition": "worn"},
        )
    )
    assert log.verify() is True

    # Mutate the first entry and ensure verification fails
    log.entries[0].payload["work_order"] = "ALTERED"
    assert log.verify() is False
