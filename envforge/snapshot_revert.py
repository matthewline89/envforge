"""Revert a snapshot to a previous state using history."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envforge.history import get_history
from envforge.snapshot import save, load


class RevertError(Exception):
    def __str__(self) -> str:
        return self.args[0]


@dataclass
class RevertResult:
    name: str
    reverted_to: str  # ISO timestamp of the history entry used
    previous_vars: dict[str, str]
    restored_vars: dict[str, str]
    keys_changed: list[str] = field(default_factory=list)

    @property
    def total_changed(self) -> int:
        return len(self.keys_changed)


def list_revert_points(name: str, snapshot_dir: Path) -> list[dict]:
    """Return history entries for *name* that contain a vars snapshot."""
    entries = get_history(snapshot_dir)
    return [
        e for e in entries
        if e.get("snapshot") == name and e.get("vars") is not None
    ]


def revert_snapshot(
    name: str,
    snapshot_dir: Path,
    index: int = 0,
    timestamp: Optional[str] = None,
) -> RevertResult:
    """Revert *name* to a previous state recorded in history.

    Args:
        name: Snapshot name.
        snapshot_dir: Directory containing snapshots.
        index: Which history entry to use (0 = most recent). Ignored when
               *timestamp* is provided.
        timestamp: ISO timestamp string to match exactly.

    Returns:
        A :class:`RevertResult` describing what changed.

    Raises:
        RevertError: If no revert points exist or the index/timestamp is invalid.
    """
    points = list_revert_points(name, snapshot_dir)
    if not points:
        raise RevertError(f"No revert points found for snapshot '{name}'")

    if timestamp is not None:
        matches = [p for p in points if p.get("timestamp") == timestamp]
        if not matches:
            raise RevertError(
                f"No history entry with timestamp '{timestamp}' for '{name}'"
            )
        entry = matches[0]
    else:
        if index >= len(points):
            raise RevertError(
                f"Index {index} out of range; only {len(points)} revert point(s) available"
            )
        entry = points[index]

    current_vars = load(name, snapshot_dir)
    restored_vars: dict[str, str] = entry["vars"]

    all_keys = set(current_vars) | set(restored_vars)
    changed = [
        k for k in all_keys if current_vars.get(k) != restored_vars.get(k)
    ]

    save(name, restored_vars, snapshot_dir)

    return RevertResult(
        name=name,
        reverted_to=entry.get("timestamp", ""),
        previous_vars=current_vars,
        restored_vars=restored_vars,
        keys_changed=sorted(changed),
    )
