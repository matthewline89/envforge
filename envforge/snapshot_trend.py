"""Track and analyse how snapshot key counts change over time."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envforge.history import get_history
from envforge.snapshot import load


@dataclass
class TrendPoint:
    timestamp: str
    key_count: int
    note: str = ""


@dataclass
class TrendReport:
    name: str
    points: List[TrendPoint] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return len(self.points) == 0

    @property
    def min_keys(self) -> int:
        return min(p.key_count for p in self.points) if self.points else 0

    @property
    def max_keys(self) -> int:
        return max(p.key_count for p in self.points) if self.points else 0

    @property
    def delta(self) -> int:
        """Change in key count from first to last recorded point."""
        if len(self.points) < 2:
            return 0
        return self.points[-1].key_count - self.points[0].key_count


def build_trend(name: str, snapshot_dir: Path) -> TrendReport:
    """Build a TrendReport for *name* using history entries that carry env vars."""
    history = get_history(snapshot_dir, name)
    points: List[TrendPoint] = []

    for entry in history:
        env = entry.get("vars")
        if env is None:
            continue
        points.append(
            TrendPoint(
                timestamp=entry.get("timestamp", ""),
                key_count=len(env),
                note=entry.get("note", ""),
            )
        )

    # Also append the current snapshot state as the latest point.
    try:
        current_env = load(name, snapshot_dir)
        from datetime import datetime, timezone

        points.append(
            TrendPoint(
                timestamp=datetime.now(timezone.utc).isoformat(),
                key_count=len(current_env),
                note="current",
            )
        )
    except FileNotFoundError:
        pass

    return TrendReport(name=name, points=points)
