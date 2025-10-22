"""Approval-style test for CSV exports."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from custody import AuditEntry
from custody.exports import export_audit_csv

APPROVAL_PATH = Path(__file__).resolve().parents[1] / "approvals" / "audit_export.approved.csv"


@pytest.mark.integration
@pytest.mark.usefixtures("frozen_time")
def test_audit_export_matches_approved_snapshot():
    entries = [
        AuditEntry(
            id=1,
            tool_id="TL-100",
            action="checkout",
            actor="u-tech",
            timestamp=datetime(2024, 1, 1, 12, 0, tzinfo=UTC),
            payload={"work_order": "WO-1"},
        ),
        AuditEntry(
            id=2,
            tool_id="TL-100",
            action="return",
            actor="u-tech",
            timestamp=datetime(2024, 1, 2, 8, 0, tzinfo=UTC),
            payload={"condition": "good"},
        ),
    ]
    csv_content, manifest = export_audit_csv(entries)

    normalized_lines = []
    for line in csv_content.strip().splitlines():
        if line.startswith("timestamp"):
            normalized_lines.append(line)
            continue
        cells = line.split(",")
        if len(cells) >= 5:
            cells[4] = "<timestamp>"
        normalized_lines.append(",".join(cells))

    approved = APPROVAL_PATH.read_text().strip().splitlines()
    assert normalized_lines == approved
    assert manifest["hash_algorithm"] == "sha256"
