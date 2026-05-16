"""Snapshot timeline: build a chronological view of snapshot events from history."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envforge.history import get_history


@dataclass
class TimelineEvent:
    snapshot: str
    action: str
    timestamp: str
    note: Optional[str] = None


@dataclass
class SnapshotTimeline:
    events: List[TimelineEvent] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.events) == 0

    def for_snapshot(self, name: str) -> "SnapshotTimeline":
        return SnapshotTimeline(
            events=[e for e in self.events if e.snapshot == name]
        )

    def sorted_events(self, descending: bool = False) -> List[TimelineEvent]:
        return sorted(self.events, key=lambda e: e.timestamp, reverse=descending)

    def actions(self) -> List[str]:
        return list({e.action for e in self.events})


def build_timeline(snapshot_dir: Path, name: Optional[str] = None) -> SnapshotTimeline:
    """Build a timeline from recorded history entries.

    If *name* is given, only events for that snapshot are included.
    """
    entries = get_history(snapshot_dir)
    events: List[TimelineEvent] = []
    for entry in entries:
        snap_name = entry.get("snapshot", "")
        if name and snap_name != name:
            continue
        events.append(
            TimelineEvent(
                snapshot=snap_name,
                action=entry.get("action", "unknown"),
                timestamp=entry.get("timestamp", ""),
                note=entry.get("note"),
            )
        )
    return SnapshotTimeline(events=events)
