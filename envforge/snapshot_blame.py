"""Track which user/process last modified each key in a snapshot."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class BlameEntry:
    key: str
    value: str
    user: str
    timestamp: str
    note: Optional[str] = None


@dataclass
class BlameReport:
    snapshot_name: str
    entries: List[BlameEntry] = field(default_factory=list)

    def for_key(self, key: str) -> Optional[BlameEntry]:
        return next((e for e in self.entries if e.key == key), None)

    def users(self) -> List[str]:
        return list({e.user for e in self.entries})


def _blame_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "blame.json"


def _load_blame(snapshot_dir: Path) -> Dict[str, dict]:
    p = _blame_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_blame(snapshot_dir: Path, data: Dict[str, dict]) -> None:
    _blame_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def record_blame(
    snapshot_dir: Path,
    snapshot_name: str,
    key: str,
    value: str,
    user: str,
    timestamp: str,
    note: Optional[str] = None,
) -> BlameEntry:
    """Record who set a specific key in a snapshot."""
    data = _load_blame(snapshot_dir)
    if snapshot_name not in data:
        data[snapshot_name] = {}
    data[snapshot_name][key] = {
        "value": value,
        "user": user,
        "timestamp": timestamp,
        "note": note,
    }
    _save_blame(snapshot_dir, data)
    return BlameEntry(key=key, value=value, user=user, timestamp=timestamp, note=note)


def get_blame(snapshot_dir: Path, snapshot_name: str) -> BlameReport:
    """Return blame information for all tracked keys in a snapshot."""
    data = _load_blame(snapshot_dir)
    raw = data.get(snapshot_name, {})
    entries = [
        BlameEntry(
            key=k,
            value=v["value"],
            user=v["user"],
            timestamp=v["timestamp"],
            note=v.get("note"),
        )
        for k, v in raw.items()
    ]
    return BlameReport(snapshot_name=snapshot_name, entries=entries)


def clear_blame(snapshot_dir: Path, snapshot_name: str) -> bool:
    """Remove all blame records for a snapshot. Returns True if anything was removed."""
    data = _load_blame(snapshot_dir)
    if snapshot_name not in data:
        return False
    del data[snapshot_name]
    _save_blame(snapshot_dir, data)
    return True
