"""Track and query snapshot access/creation history."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

HISTORY_FILE = "history.json"


def _load_history(snapshot_dir: Path) -> List[dict]:
    path = snapshot_dir / HISTORY_FILE
    if not path.exists():
        return []
    with path.open("r") as f:
        return json.load(f)


def _save_history(snapshot_dir: Path, entries: List[dict]) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    path = snapshot_dir / HISTORY_FILE
    with path.open("w") as f:
        json.dump(entries, f, indent=2)


def record_event(
    snapshot_dir: Path,
    snapshot_name: str,
    action: str,
    note: Optional[str] = None,
) -> dict:
    """Append an event to the history log and return the new entry."""
    entries = _load_history(snapshot_dir)
    entry = {
        "snapshot": snapshot_name,
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if note:
        entry["note"] = note
    entries.append(entry)
    _save_history(snapshot_dir, entries)
    return entry


def get_history(
    snapshot_dir: Path,
    snapshot_name: Optional[str] = None,
    action: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[dict]:
    """Return history entries, optionally filtered by snapshot name or action."""
    entries = _load_history(snapshot_dir)
    if snapshot_name:
        entries = [e for e in entries if e.get("snapshot") == snapshot_name]
    if action:
        entries = [e for e in entries if e.get("action") == action]
    if limit is not None:
        entries = entries[-limit:]
    return entries


def clear_history(snapshot_dir: Path, snapshot_name: Optional[str] = None) -> int:
    """Remove history entries. If snapshot_name given, remove only those entries.
    Returns the number of entries removed."""
    entries = _load_history(snapshot_dir)
    if snapshot_name:
        kept = [e for e in entries if e.get("snapshot") != snapshot_name]
    else:
        kept = []
    removed = len(entries) - len(kept)
    _save_history(snapshot_dir, kept)
    return removed


def get_last_event(
    snapshot_dir: Path,
    snapshot_name: str,
    action: Optional[str] = None,
) -> Optional[dict]:
    """Return the most recent history entry for a given snapshot.

    Args:
        snapshot_dir: Directory where the history file is stored.
        snapshot_name: Name of the snapshot to look up.
        action: If provided, restrict to entries with this action type.

    Returns:
        The most recent matching entry, or ``None`` if no entries exist.
    """
    entries = get_history(snapshot_dir, snapshot_name=snapshot_name, action=action)
    return entries[-1] if entries else None
