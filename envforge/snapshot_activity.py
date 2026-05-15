"""Track and report snapshot activity (reads, writes, deletes) over time."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


@dataclass
class ActivityEntry:
    snapshot: str
    action: str  # "read" | "write" | "delete"
    timestamp: str
    user: Optional[str] = None


@dataclass
class ActivityReport:
    entries: List[ActivityEntry] = field(default_factory=list)

    def for_snapshot(self, name: str) -> "ActivityReport":
        return ActivityReport([e for e in self.entries if e.snapshot == name])

    def by_action(self, action: str) -> "ActivityReport":
        return ActivityReport([e for e in self.entries if e.action == action])

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def most_recent(self) -> Optional[ActivityEntry]:
        return self.entries[-1] if self.entries else None


def _activity_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "activity.json"


def _load_activity(snapshot_dir: Path) -> List[dict]:
    path = _activity_path(snapshot_dir)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_activity(snapshot_dir: Path, entries: List[dict]) -> None:
    _activity_path(snapshot_dir).write_text(json.dumps(entries, indent=2))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_activity(
    snapshot_dir: Path,
    snapshot: str,
    action: str,
    user: Optional[str] = None,
) -> ActivityEntry:
    entries = _load_activity(snapshot_dir)
    entry = ActivityEntry(
        snapshot=snapshot,
        action=action,
        timestamp=_now_iso(),
        user=user,
    )
    entries.append({
        "snapshot": entry.snapshot,
        "action": entry.action,
        "timestamp": entry.timestamp,
        "user": entry.user,
    })
    _save_activity(snapshot_dir, entries)
    return entry


def get_activity(snapshot_dir: Path, snapshot: Optional[str] = None) -> ActivityReport:
    raw = _load_activity(snapshot_dir)
    entries = [
        ActivityEntry(
            snapshot=r["snapshot"],
            action=r["action"],
            timestamp=r["timestamp"],
            user=r.get("user"),
        )
        for r in raw
    ]
    report = ActivityReport(entries)
    if snapshot:
        return report.for_snapshot(snapshot)
    return report


def clear_activity(snapshot_dir: Path, snapshot: Optional[str] = None) -> int:
    if snapshot is None:
        count = len(_load_activity(snapshot_dir))
        _save_activity(snapshot_dir, [])
        return count
    raw = _load_activity(snapshot_dir)
    kept = [r for r in raw if r["snapshot"] != snapshot]
    removed = len(raw) - len(kept)
    _save_activity(snapshot_dir, kept)
    return removed
