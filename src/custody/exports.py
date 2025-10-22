"""CSV export helpers with deterministic ordering."""

from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Iterable, Tuple

from .models import AuditEntry


EXPORT_HEADERS = ["id", "tool_id", "action", "actor", "timestamp", "payload"]


def export_audit_csv(entries: Iterable[AuditEntry]) -> Tuple[str, dict]:
    """Serialise audit entries into CSV along with a manifest stub."""

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=EXPORT_HEADERS)
    writer.writeheader()
    rows = []
    for entry in entries:
        row = {
            "id": entry.id,
            "tool_id": entry.tool_id,
            "action": entry.action,
            "actor": entry.actor,
            "timestamp": entry.timestamp.isoformat(),
            "payload": ";".join(f"{k}={v}" for k, v in sorted(entry.payload.items())),
        }
        rows.append(row)
    rows.sort(key=lambda item: (item["tool_id"], item["id"]))
    for row in rows:
        writer.writerow(row)
    manifest = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "record_count": len(rows),
        "hash_algorithm": "sha256",
        # TODO: replace with signed manifest once available
    }
    return buffer.getvalue(), manifest
