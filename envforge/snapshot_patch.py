"""Apply a partial patch (key additions, updates, deletions) to a snapshot."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envforge.snapshot import load, save


class PatchError(Exception):
    def __str__(self) -> str:  # pragma: no cover
        return self.args[0]


@dataclass
class PatchResult:
    name: str
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    deleted: List[str] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.updated) + len(self.deleted)


def patch_snapshot(
    name: str,
    snapshot_dir: str,
    *,
    set_vars: Optional[Dict[str, str]] = None,
    delete_keys: Optional[List[str]] = None,
) -> PatchResult:
    """Apply a patch to an existing snapshot in-place.

    Args:
        name: Snapshot name (without .json extension).
        snapshot_dir: Directory containing snapshots.
        set_vars: Keys to add or update.
        delete_keys: Keys to remove.

    Returns:
        A PatchResult describing what changed.

    Raises:
        PatchError: If the snapshot does not exist.
    """
    try:
        env = load(name, snapshot_dir)
    except FileNotFoundError:
        raise PatchError(f"Snapshot '{name}' not found in {snapshot_dir}")

    result = PatchResult(name=name)

    for key, value in (set_vars or {}).items():
        if key in env:
            result.updated.append(key)
        else:
            result.added.append(key)
        env[key] = value

    for key in delete_keys or []:
        if key in env:
            del env[key]
            result.deleted.append(key)

    save(name, env, snapshot_dir)
    return result
