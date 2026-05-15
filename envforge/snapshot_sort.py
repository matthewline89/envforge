"""Sort snapshots by various criteria."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Literal

from envforge.snapshot import load, list_snapshots

SortKey = Literal["name", "size", "keys", "mtime"]


@dataclass
class SortedSnapshot:
    name: str
    key_count: int
    mtime: float
    size_bytes: int


@dataclass
class SortResult:
    items: List[SortedSnapshot] = field(default_factory=list)
    sort_key: str = "name"
    ascending: bool = True


def _snapshot_mtime(snapshot_dir: Path, name: str) -> float:
    p = snapshot_dir / f"{name}.json"
    return p.stat().st_mtime if p.exists() else 0.0


def _snapshot_size(snapshot_dir: Path, name: str) -> int:
    p = snapshot_dir / f"{name}.json"
    return p.stat().st_size if p.exists() else 0


def sort_snapshots(
    snapshot_dir: Path,
    sort_key: SortKey = "name",
    ascending: bool = True,
) -> SortResult:
    """Return snapshots sorted by the given key."""
    names = list_snapshots(snapshot_dir)
    items: List[SortedSnapshot] = []

    for name in names:
        try:
            env = load(snapshot_dir, name)
        except Exception:
            env = {}
        items.append(
            SortedSnapshot(
                name=name,
                key_count=len(env),
                mtime=_snapshot_mtime(snapshot_dir, name),
                size_bytes=_snapshot_size(snapshot_dir, name),
            )
        )

    key_fn = {
        "name": lambda s: s.name,
        "size": lambda s: s.size_bytes,
        "keys": lambda s: s.key_count,
        "mtime": lambda s: s.mtime,
    }.get(sort_key, lambda s: s.name)

    items.sort(key=key_fn, reverse=not ascending)
    return SortResult(items=items, sort_key=sort_key, ascending=ascending)
