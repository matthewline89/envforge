"""Spotlight: surface the most notable snapshots based on activity, rating, and recency."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envforge.snapshot import list_snapshots
from envforge.snapshot_rating import get_rating
from envforge.snapshot_access import get_access
from envforge.snapshot_stats import compute_stats


@dataclass
class SpotlightEntry:
    name: str
    score: float
    rating: int
    access_count: int
    key_count: int


@dataclass
class SpotlightReport:
    entries: List[SpotlightEntry] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def top(self, n: int = 5) -> List[SpotlightEntry]:
        return sorted(self.entries, key=lambda e: e.score, reverse=True)[:n]


def _compute_score(rating: int, access_count: int, key_count: int) -> float:
    """Weighted score combining rating, access frequency, and size."""
    return rating * 2.0 + access_count * 1.5 + min(key_count, 50) * 0.1


def compute_spotlight(snapshot_dir: Path) -> SpotlightReport:
    """Build a spotlight report for all snapshots in *snapshot_dir*."""
    names = list_snapshots(snapshot_dir)
    entries: List[SpotlightEntry] = []

    for name in names:
        try:
            stats = compute_stats(snapshot_dir, name)
            key_count = stats.total_keys
        except Exception:
            key_count = 0

        rating = get_rating(snapshot_dir, name) or 0

        access = get_access(snapshot_dir, name)
        access_count = access.count if access else 0

        score = _compute_score(rating, access_count, key_count)
        entries.append(
            SpotlightEntry(
                name=name,
                score=score,
                rating=rating,
                access_count=access_count,
                key_count=key_count,
            )
        )

    return SpotlightReport(entries=entries)
