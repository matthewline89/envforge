"""Group management: assign snapshots to named groups and query them."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class GroupError(Exception):
    """Raised when a group operation cannot be completed."""


def _groups_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "groups.json"


def _load_groups(snapshot_dir: Path) -> Dict[str, List[str]]:
    path = _groups_path(snapshot_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_groups(snapshot_dir: Path, data: Dict[str, List[str]]) -> None:
    _groups_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def add_to_group(snapshot_dir: Path, group: str, snapshot: str) -> bool:
    """Add *snapshot* to *group*. Returns True if newly added, False if already present."""
    data = _load_groups(snapshot_dir)
    members = data.setdefault(group, [])
    if snapshot in members:
        return False
    members.append(snapshot)
    _save_groups(snapshot_dir, data)
    return True


def remove_from_group(snapshot_dir: Path, group: str, snapshot: str) -> bool:
    """Remove *snapshot* from *group*. Returns True if removed, False if not found."""
    data = _load_groups(snapshot_dir)
    members = data.get(group, [])
    if snapshot not in members:
        return False
    members.remove(snapshot)
    if not members:
        del data[group]
    _save_groups(snapshot_dir, data)
    return True


def list_groups(snapshot_dir: Path) -> Dict[str, List[str]]:
    """Return all groups and their member snapshots."""
    return _load_groups(snapshot_dir)


def get_group(snapshot_dir: Path, group: str) -> Optional[List[str]]:
    """Return members of *group*, or None if the group does not exist."""
    data = _load_groups(snapshot_dir)
    return data.get(group)


def delete_group(snapshot_dir: Path, group: str) -> bool:
    """Delete an entire group. Returns True if deleted, False if not found."""
    data = _load_groups(snapshot_dir)
    if group not in data:
        return False
    del data[group]
    _save_groups(snapshot_dir, data)
    return True
