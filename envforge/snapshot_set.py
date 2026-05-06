"""Snapshot set management — group snapshots into named sets and operate on them collectively."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional


class SnapshotSetError(Exception):
    pass


def _sets_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "_snapshot_sets.json"


def _load_sets(snapshot_dir: Path) -> dict:
    path = _sets_path(snapshot_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_sets(snapshot_dir: Path, data: dict) -> None:
    _sets_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def create_set(snapshot_dir: Path, name: str, members: List[str]) -> bool:
    """Create a named snapshot set. Returns True if new, False if overwritten."""
    data = _load_sets(snapshot_dir)
    is_new = name not in data
    data[name] = list(dict.fromkeys(members))  # deduplicate, preserve order
    _save_sets(snapshot_dir, data)
    return is_new


def delete_set(snapshot_dir: Path, name: str) -> bool:
    """Remove a named set. Returns True if it existed."""
    data = _load_sets(snapshot_dir)
    if name not in data:
        return False
    del data[name]
    _save_sets(snapshot_dir, data)
    return True


def get_set(snapshot_dir: Path, name: str) -> Optional[List[str]]:
    """Return members of a named set, or None if it doesn't exist."""
    return _load_sets(snapshot_dir).get(name)


def list_sets(snapshot_dir: Path) -> dict:
    """Return all snapshot sets as {name: [members]}."""
    return _load_sets(snapshot_dir)


def add_to_set(snapshot_dir: Path, name: str, snapshot: str) -> bool:
    """Add a snapshot to an existing set. Returns True if newly added."""
    data = _load_sets(snapshot_dir)
    if name not in data:
        raise SnapshotSetError(f"Set '{name}' does not exist.")
    if snapshot in data[name]:
        return False
    data[name].append(snapshot)
    _save_sets(snapshot_dir, data)
    return True


def remove_from_set(snapshot_dir: Path, name: str, snapshot: str) -> bool:
    """Remove a snapshot from a set. Returns True if it was present."""
    data = _load_sets(snapshot_dir)
    if name not in data or snapshot not in data[name]:
        return False
    data[name].remove(snapshot)
    _save_sets(snapshot_dir, data)
    return True
