"""Track and retrieve a history of diffs between snapshots."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from envforge.diff import DiffResult, diff_snapshots


@dataclass
class DiffHistoryEntry:
    id: int
    snapshot_a: str
    snapshot_b: str
    timestamp: str
    added: Dict[str, str]
    removed: Dict[str, str]
    changed: Dict[str, List[str]]
    note: Optional[str] = None


@dataclass
class DiffHistory:
    entries: List[DiffHistoryEntry] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.entries)

    def is_empty(self) -> bool:
        return len(self.entries) == 0


def _diff_history_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "diff_history.json"


def _load_history(snapshot_dir: Path) -> List[dict]:
    path = _diff_history_path(snapshot_dir)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_history(snapshot_dir: Path, entries: List[dict]) -> None:
    _diff_history_path(snapshot_dir).write_text(json.dumps(entries, indent=2))


def record_diff(
    snapshot_dir: Path,
    name_a: str,
    name_b: str,
    note: Optional[str] = None,
) -> DiffHistoryEntry:
    result: DiffResult = diff_snapshots(snapshot_dir, name_a, name_b)
    entries = _load_history(snapshot_dir)
    entry_id = (max(e["id"] for e in entries) + 1) if entries else 1
    timestamp = datetime.now(timezone.utc).isoformat()
    record = {
        "id": entry_id,
        "snapshot_a": name_a,
        "snapshot_b": name_b,
        "timestamp": timestamp,
        "added": result.added,
        "removed": result.removed,
        "changed": {k: list(v) for k, v in result.changed.items()},
        "note": note,
    }
    entries.append(record)
    _save_history(snapshot_dir, entries)
    return DiffHistoryEntry(**record)


def get_diff_history(
    snapshot_dir: Path,
    snapshot_name: Optional[str] = None,
) -> DiffHistory:
    raw = _load_history(snapshot_dir)
    if snapshot_name:
        raw = [
            e for e in raw
            if e["snapshot_a"] == snapshot_name or e["snapshot_b"] == snapshot_name
        ]
    return DiffHistory(entries=[DiffHistoryEntry(**e) for e in raw])


def clear_diff_history(snapshot_dir: Path) -> int:
    entries = _load_history(snapshot_dir)
    count = len(entries)
    _save_history(snapshot_dir, [])
    return count
