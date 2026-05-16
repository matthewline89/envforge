"""Track and rank snapshots by popularity based on access and activity."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envforge.snapshot_access import _access_path, _load_access
from envforge.snapshot_activity import _activity_path, _load_activity


@dataclass
class PopularityEntry:
    name: str
    access_count: int
    activity_count: int
    score: float


@dataclass
class PopularityReport:
    entries: List[PopularityEntry] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def top(self, n: int = 5) -> List[PopularityEntry]:
        return sorted(self.entries, key=lambda e: e.score, reverse=True)[:n]

    def rank_of(self, name: str) -> int | None:
        ranked = sorted(self.entries, key=lambda e: e.score, reverse=True)
        for i, entry in enumerate(ranked, start=1):
            if entry.name == name:
                return i
        return None


def _compute_score(access_count: int, activity_count: int) -> float:
    """Weighted score: access counts more than activity events."""
    return round(access_count * 2.0 + activity_count * 1.0, 2)


def compute_popularity(snapshot_dir: Path) -> PopularityReport:
    """Build a popularity report from access and activity data."""
    access_data = _load_access(snapshot_dir)
    activity_data = _load_activity(snapshot_dir)

    names: set[str] = set(access_data.keys()) | set(activity_data.keys())

    entries: List[PopularityEntry] = []
    for name in names:
        access_count = access_data.get(name, {}).get("count", 0)
        activity_count = len(activity_data.get(name, []))
        score = _compute_score(access_count, activity_count)
        entries.append(
            PopularityEntry(
                name=name,
                access_count=access_count,
                activity_count=activity_count,
                score=score,
            )
        )

    return PopularityReport(entries=entries)
