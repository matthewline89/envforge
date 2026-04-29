"""Audit log: record and query who accessed or modified snapshots."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

_AUDIT_FILE = "audit_log.json"


@dataclass
class AuditEntry:
    action: str
    snapshot: str
    user: str
    timestamp: str
    note: Optional[str] = None


def _audit_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _AUDIT_FILE


def _load_entries(snapshot_dir: Path) -> List[dict]:
    path = _audit_path(snapshot_dir)
    if not path.exists():
        return []
    with path.open() as fh:
        return json.load(fh)


def _save_entries(snapshot_dir: Path, entries: List[dict]) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    with _audit_path(snapshot_dir).open("w") as fh:
        json.dump(entries, fh, indent=2)


def record_action(
    snapshot_dir: Path,
    action: str,
    snapshot: str,
    note: Optional[str] = None,
    user: Optional[str] = None,
) -> AuditEntry:
    """Append an audit entry and return it."""
    resolved_user = user or os.environ.get("USER", os.environ.get("USERNAME", "unknown"))
    entry = AuditEntry(
        action=action,
        snapshot=snapshot,
        user=resolved_user,
        timestamp=datetime.now(timezone.utc).isoformat(),
        note=note,
    )
    entries = _load_entries(snapshot_dir)
    entries.append(entry.__dict__)
    _save_entries(snapshot_dir, entries)
    return entry


def get_audit_log(
    snapshot_dir: Path,
    snapshot: Optional[str] = None,
    action: Optional[str] = None,
) -> List[AuditEntry]:
    """Return audit entries, optionally filtered by snapshot name or action."""
    entries = _load_entries(snapshot_dir)
    results = []
    for raw in entries:
        if snapshot and raw.get("snapshot") != snapshot:
            continue
        if action and raw.get("action") != action:
            continue
        results.append(AuditEntry(**raw))
    return results


def clear_audit_log(snapshot_dir: Path) -> int:
    """Delete all audit entries. Returns count of removed entries."""
    entries = _load_entries(snapshot_dir)
    count = len(entries)
    _save_entries(snapshot_dir, [])
    return count
