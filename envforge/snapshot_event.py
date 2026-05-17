"""Snapshot event log — record and query discrete events tied to a snapshot."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


@dataclass
class EventEntry:
    snapshot: str
    event: str
    timestamp: str
    user: Optional[str] = None
    note: Optional[str] = None


@dataclass
class EventLog:
    entries: List[EventEntry] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.entries)

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def for_snapshot(self, name: str) -> List[EventEntry]:
        return [e for e in self.entries if e.snapshot == name]

    def by_event(self, event: str) -> List[EventEntry]:
        return [e for e in self.entries if e.event == event]


def _event_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "_events.json"


def _load_events(snapshot_dir: Path) -> List[dict]:
    p = _event_path(snapshot_dir)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_events(snapshot_dir: Path, data: List[dict]) -> None:
    _event_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_event(
    snapshot_dir: Path,
    snapshot: str,
    event: str,
    user: Optional[str] = None,
    note: Optional[str] = None,
) -> EventEntry:
    data = _load_events(snapshot_dir)
    entry = EventEntry(
        snapshot=snapshot,
        event=event,
        timestamp=_now_iso(),
        user=user,
        note=note,
    )
    data.append(entry.__dict__)
    _save_events(snapshot_dir, data)
    return entry


def get_event_log(snapshot_dir: Path) -> EventLog:
    data = _load_events(snapshot_dir)
    return EventLog(entries=[EventEntry(**d) for d in data])


def clear_events(snapshot_dir: Path, snapshot: Optional[str] = None) -> int:
    data = _load_events(snapshot_dir)
    if snapshot is None:
        removed = len(data)
        _save_events(snapshot_dir, [])
        return removed
    kept = [d for d in data if d["snapshot"] != snapshot]
    removed = len(data) - len(kept)
    _save_events(snapshot_dir, kept)
    return removed
