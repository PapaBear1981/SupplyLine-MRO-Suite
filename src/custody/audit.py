"""Append-only audit log with optional hash chaining."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable, List

from .models import AuditEntry


@dataclass
class _AuditState:
    entries: List[AuditEntry]


class AuditLog:
    """In-memory append-only audit log used in integration tests."""

    def __init__(self, entries: Iterable[AuditEntry] | None = None, *, enable_hash_chain: bool = True) -> None:
        self._state = _AuditState(entries=list(entries or []))
        self._enable_hash_chain = enable_hash_chain
        if self._enable_hash_chain:
            self._rehash()

    @property
    def entries(self) -> List[AuditEntry]:
        return list(self._state.entries)

    def append(self, entry: AuditEntry) -> AuditEntry:
        if self._state.entries and entry.id <= self._state.entries[-1].id:
            raise ValueError("Audit entries must be strictly increasing ids")
        if self._enable_hash_chain:
            previous_hash = self._state.entries[-1].entry_hash if self._state.entries else None
            entry.previous_hash = previous_hash
            entry.entry_hash = self._hash(entry)
        self._state.entries.append(entry)
        return entry

    def verify(self) -> bool:
        if not self._enable_hash_chain:
            return True
        expected_previous = None
        for entry in self._state.entries:
            if entry.previous_hash != expected_previous:
                return False
            calculated = self._hash(entry)
            if calculated != entry.entry_hash:
                return False
            expected_previous = entry.entry_hash
        return True

    def _rehash(self) -> None:
        expected_previous = None
        for entry in self._state.entries:
            entry.previous_hash = expected_previous
            entry.entry_hash = self._hash(entry)
            expected_previous = entry.entry_hash

    @staticmethod
    def _hash(entry: AuditEntry) -> str:
        digest = hashlib.sha256()
        digest.update(str(entry.id).encode())
        digest.update(entry.tool_id.encode())
        digest.update(entry.action.encode())
        digest.update(entry.actor.encode())
        digest.update(str(entry.timestamp.timestamp()).encode())
        digest.update(str(sorted(entry.payload.items())).encode())
        if entry.previous_hash:
            digest.update(entry.previous_hash.encode())
        return digest.hexdigest()
