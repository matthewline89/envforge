"""Track and query last-access timestamps for snapshots."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


_ACCESS_FILE = "access.json"


@dataclass
class AccessEntry:
    name: str
    last_accessed: str  # ISO-8601
    access_count: int


def _access_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _ACCESS_FILE


def _load_access(snapshot_dir: Path) -> Dict[str, dict]:
    path = _access_path(snapshot_dir)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_access(snapshot_dir: Path, data: Dict[str, dict]) -> None:
    path = _access_path(snapshot_dir)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_access(snapshot_dir: Path, name: str) -> AccessEntry:
    """Record an access event for *name* and return the updated entry."""
    data = _load_access(snapshot_dir)
    existing = data.get(name, {"access_count": 0})
    entry = {
        "last_accessed": _now_iso(),
        "access_count": existing["access_count"] + 1,
    }
    data[name] = entry
    _save_access(snapshot_dir, data)
    return AccessEntry(name=name, **entry)


def get_access(snapshot_dir: Path, name: str) -> Optional[AccessEntry]:
    """Return the access entry for *name*, or *None* if never accessed."""
    data = _load_access(snapshot_dir)
    raw = data.get(name)
    if raw is None:
        return None
    return AccessEntry(name=name, **raw)


def list_access(snapshot_dir: Path) -> List[AccessEntry]:
    """Return all access entries sorted by last_accessed descending."""
    data = _load_access(snapshot_dir)
    entries = [AccessEntry(name=n, **v) for n, v in data.items()]
    return sorted(entries, key=lambda e: e.last_accessed, reverse=True)


def reset_access(snapshot_dir: Path, name: str) -> bool:
    """Remove the access record for *name*. Returns True if it existed."""
    data = _load_access(snapshot_dir)
    if name not in data:
        return False
    del data[name]
    _save_access(snapshot_dir, data)
    return True
