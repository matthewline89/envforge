"""Trigger module: define and fire named triggers that auto-snapshot on condition."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from envforge.snapshot import capture, save


@dataclass
class TriggerEntry:
    name: str
    condition: str  # e.g. "key_added", "key_removed", "value_changed"
    target_key: Optional[str] = None
    snapshot_prefix: str = "trigger"


@dataclass
class TriggerResult:
    triggered: bool
    snapshot_name: Optional[str] = None
    entry: Optional[TriggerEntry] = None
    note: str = ""


def _triggers_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "triggers.json"


def _load_triggers(snapshot_dir: Path) -> List[Dict]:
    path = _triggers_path(snapshot_dir)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_triggers(snapshot_dir: Path, entries: List[Dict]) -> None:
    _triggers_path(snapshot_dir).write_text(json.dumps(entries, indent=2))


def add_trigger(snapshot_dir: Path, entry: TriggerEntry) -> bool:
    """Register a trigger. Returns True if new, False if replaced."""
    entries = _load_triggers(snapshot_dir)
    existing = [e for e in entries if e["name"] != entry.name]
    is_new = len(existing) == len(entries)
    existing.append({
        "name": entry.name,
        "condition": entry.condition,
        "target_key": entry.target_key,
        "snapshot_prefix": entry.snapshot_prefix,
    })
    _save_triggers(snapshot_dir, existing)
    return is_new


def remove_trigger(snapshot_dir: Path, name: str) -> bool:
    """Remove a trigger by name. Returns True if found and removed."""
    entries = _load_triggers(snapshot_dir)
    remaining = [e for e in entries if e["name"] != name]
    if len(remaining) == len(entries):
        return False
    _save_triggers(snapshot_dir, remaining)
    return True


def list_triggers(snapshot_dir: Path) -> List[TriggerEntry]:
    return [
        TriggerEntry(
            name=e["name"],
            condition=e["condition"],
            target_key=e.get("target_key"),
            snapshot_prefix=e.get("snapshot_prefix", "trigger"),
        )
        for e in _load_triggers(snapshot_dir)
    ]


def evaluate_trigger(
    snapshot_dir: Path,
    entry: TriggerEntry,
    before: Dict[str, str],
    after: Dict[str, str],
    version: Optional[str] = None,
) -> TriggerResult:
    """Evaluate a single trigger against before/after env dicts."""
    fired = False
    key = entry.target_key

    if entry.condition == "key_added":
        candidates = set(after) - set(before)
        fired = (key in candidates) if key else bool(candidates)
    elif entry.condition == "key_removed":
        candidates = set(before) - set(after)
        fired = (key in candidates) if key else bool(candidates)
    elif entry.condition == "value_changed":
        changed = {k for k in set(before) & set(after) if before[k] != after[k]}
        fired = (key in changed) if key else bool(changed)

    if not fired:
        return TriggerResult(triggered=False, entry=entry)

    import datetime
    ts = (version or datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"))
    snap_name = f"{entry.snapshot_prefix}-{entry.name}-{ts}"
    save(snapshot_dir, snap_name, after)
    return TriggerResult(triggered=True, snapshot_name=snap_name, entry=entry,
                         note=f"Condition '{entry.condition}' fired.")
