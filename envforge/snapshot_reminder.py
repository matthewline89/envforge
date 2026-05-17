"""Snapshot reminder: schedule reminders tied to snapshot names."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ReminderEntry:
    snapshot: str
    message: str
    due: str  # ISO-8601 date string
    recur: Optional[str] = None  # e.g. "daily", "weekly"


@dataclass
class ReminderReport:
    entries: List[ReminderEntry] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def for_snapshot(self, name: str) -> List[ReminderEntry]:
        return [e for e in self.entries if e.snapshot == name]

    def due_before(self, cutoff: str) -> List[ReminderEntry]:
        return [e for e in self.entries if e.due <= cutoff]


def _reminders_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "reminders.json"


def _load_reminders(snapshot_dir: Path) -> Dict:
    p = _reminders_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_reminders(snapshot_dir: Path, data: Dict) -> None:
    _reminders_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def add_reminder(
    snapshot_dir: Path,
    snapshot: str,
    message: str,
    due: str,
    recur: Optional[str] = None,
) -> bool:
    """Add a reminder for *snapshot*. Returns True when newly created."""
    data = _load_reminders(snapshot_dir)
    entries = data.get(snapshot, [])
    for entry in entries:
        if entry["due"] == due and entry["message"] == message:
            return False
    entries.append({"message": message, "due": due, "recur": recur})
    data[snapshot] = entries
    _save_reminders(snapshot_dir, data)
    return True


def remove_reminder(snapshot_dir: Path, snapshot: str, due: str) -> bool:
    """Remove reminder matching *snapshot* + *due*. Returns True if found."""
    data = _load_reminders(snapshot_dir)
    entries = data.get(snapshot, [])
    new_entries = [e for e in entries if e["due"] != due]
    if len(new_entries) == len(entries):
        return False
    data[snapshot] = new_entries
    _save_reminders(snapshot_dir, data)
    return True


def get_reminders(snapshot_dir: Path) -> ReminderReport:
    """Return all reminders as a :class:`ReminderReport`."""
    data = _load_reminders(snapshot_dir)
    entries: List[ReminderEntry] = []
    for snap, items in data.items():
        for item in items:
            entries.append(
                ReminderEntry(
                    snapshot=snap,
                    message=item["message"],
                    due=item["due"],
                    recur=item.get("recur"),
                )
            )
    entries.sort(key=lambda e: e.due)
    return ReminderReport(entries=entries)
