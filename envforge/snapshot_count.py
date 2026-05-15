"""Snapshot count tracking — count env vars across snapshots with filtering."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envforge.snapshot import load, list_snapshots


@dataclass
class CountEntry:
    name: str
    total: int
    empty: int
    non_empty: int


@dataclass
class CountReport:
    entries: list[CountEntry] = field(default_factory=list)

    @property
    def total_snapshots(self) -> int:
        return len(self.entries)

    @property
    def grand_total_keys(self) -> int:
        return sum(e.total for e in self.entries)

    @property
    def grand_total_empty(self) -> int:
        return sum(e.empty for e in self.entries)


def count_snapshot(name: str, snapshot_dir: Path) -> CountEntry:
    """Return a CountEntry for a single snapshot."""
    env = load(name, snapshot_dir)
    empty = sum(1 for v in env.values() if v == "")
    return CountEntry(
        name=name,
        total=len(env),
        empty=empty,
        non_empty=len(env) - empty,
    )


def count_all(
    snapshot_dir: Path,
    min_keys: Optional[int] = None,
    max_keys: Optional[int] = None,
) -> CountReport:
    """Build a CountReport for all snapshots, with optional key-count filtering."""
    report = CountReport()
    for name in list_snapshots(snapshot_dir):
        entry = count_snapshot(name, snapshot_dir)
        if min_keys is not None and entry.total < min_keys:
            continue
        if max_keys is not None and entry.total > max_keys:
            continue
        report.entries.append(entry)
    return report
