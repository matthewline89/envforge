"""Snapshot expiration: set TTL on snapshots and query/purge expired ones."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


_EXPIRY_FILE = "expiry.json"


def _expiry_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _EXPIRY_FILE


def _load_expiry(snapshot_dir: Path) -> dict[str, str]:
    path = _expiry_path(snapshot_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_expiry(snapshot_dir: Path, data: dict[str, str]) -> None:
    _expiry_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ExpireResult:
    removed: list[str] = field(default_factory=list)

    @property
    def total_removed(self) -> int:
        return len(self.removed)


def set_expiry(snapshot_dir: Path, name: str, expires_at: datetime) -> None:
    """Attach an expiration timestamp (UTC) to a snapshot."""
    data = _load_expiry(snapshot_dir)
    data[name] = expires_at.astimezone(timezone.utc).isoformat()
    _save_expiry(snapshot_dir, data)


def get_expiry(snapshot_dir: Path, name: str) -> Optional[datetime]:
    """Return the expiration datetime for *name*, or None if not set."""
    data = _load_expiry(snapshot_dir)
    raw = data.get(name)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def is_expired(snapshot_dir: Path, name: str) -> bool:
    """Return True if the snapshot has passed its expiration time."""
    exp = get_expiry(snapshot_dir, name)
    if exp is None:
        return False
    return datetime.now(timezone.utc) >= exp


def list_expiry(snapshot_dir: Path) -> dict[str, datetime]:
    """Return all name → expiration mappings."""
    return {
        name: datetime.fromisoformat(raw)
        for name, raw in _load_expiry(snapshot_dir).items()
    }


def purge_expired(snapshot_dir: Path) -> ExpireResult:
    """Delete snapshot files that have passed their expiration time."""
    result = ExpireResult()
    data = _load_expiry(snapshot_dir)
    now = datetime.now(timezone.utc)
    to_remove: list[str] = []

    for name, raw in data.items():
        if now >= datetime.fromisoformat(raw):
            snap_file = snapshot_dir / f"{name}.json"
            if snap_file.exists():
                snap_file.unlink()
            to_remove.append(name)
            result.removed.append(name)

    for name in to_remove:
        del data[name]
    _save_expiry(snapshot_dir, data)
    return result
