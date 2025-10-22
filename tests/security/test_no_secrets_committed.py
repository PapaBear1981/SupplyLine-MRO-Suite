"""Sanity checks for obvious committed secrets.

These tests do not replace gitleaks but provide a quick signal when running
``pytest -m security`` locally.
"""

from __future__ import annotations

from pathlib import Path

import pytest

SUSPICIOUS_PATTERNS = [
    "BEGIN PRIVATE KEY",
    "AWS_SECRET_ACCESS_KEY",
    "-----BEGIN OPENSSH PRIVATE KEY-----",
]


@pytest.mark.security
def test_repository_has_no_private_key_material():
    repo_root = Path(__file__).resolve().parents[2]
    offenders: list[Path] = []
    for path in repo_root.rglob("*"):
        if path.is_dir() or path.suffix in {".png", ".jpg", ".jpeg", ".gif", ".svg"}:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        if any(pattern in content for pattern in SUSPICIOUS_PATTERNS):
            offenders.append(path.relative_to(repo_root))
    assert not offenders, f"Potential secrets detected in: {offenders}"
