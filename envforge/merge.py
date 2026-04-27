"""Merge two or more snapshots into a single combined snapshot."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envforge.snapshot import load, save


@dataclass
class MergeResult:
    merged: Dict[str, str] = field(default_factory=dict)
    conflicts: Dict[str, List[str]] = field(default_factory=dict)  # key -> [val_a, val_b]
    sources: List[str] = field(default_factory=list)


def merge_dicts(
    base: Dict[str, str],
    override: Dict[str, str],
    conflicts: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, str]:
    """Merge *override* into *base*, recording conflicts when values differ."""
    result = dict(base)
    for key, value in override.items():
        if key in result and result[key] != value:
            if conflicts is not None:
                conflicts[key] = [result[key], value]
        result[key] = value
    return result


def merge_snapshots(
    snapshot_names: List[str],
    snapshot_dir: str,
    strategy: str = "last-wins",
) -> MergeResult:
    """Load and merge multiple snapshots in order.

    strategy:
        - ``last-wins``  : later snapshot values overwrite earlier ones (default).
        - ``first-wins`` : earlier snapshot values are preserved.
    """
    if len(snapshot_names) < 2:
        raise ValueError("At least two snapshot names are required for a merge.")

    result = MergeResult(sources=list(snapshot_names))
    snapshots = [load(name, snapshot_dir) for name in snapshot_names]

    if strategy == "first-wins":
        snapshots = list(reversed(snapshots))

    merged: Dict[str, str] = {}
    for snap in snapshots:
        merged = merge_dicts(merged, snap, result.conflicts)

    result.merged = merged
    return result


def save_merge(
    merge_result: MergeResult,
    output_name: str,
    snapshot_dir: str,
) -> str:
    """Persist a MergeResult as a new snapshot and return the file path."""
    return save(merge_result.merged, output_name, snapshot_dir)
