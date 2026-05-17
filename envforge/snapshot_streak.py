"""Track consecutive daily snapshot activity streaks."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import List


@dataclass
class StreakEntry:
    snapshot: str
    date: str  # ISO date YYYY-MM-DD


@dataclass
class StreakReport:
    snapshot: str
    dates: List[str] = field(default_factory=list)
    current_streak: int = 0
    longest_streak: int = 0

    def is_empty(self) -> bool:
        return len(self.dates) == 0


def _streak_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "streaks.json"


def _load_streaks(snapshot_dir: Path) -> dict:
    p = _streak_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_streaks(snapshot_dir: Path, data: dict) -> None:
    _streak_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def record_activity(snapshot_dir: Path, snapshot: str, on_date: str | None = None) -> StreakEntry:
    """Record that a snapshot was active on a given date (defaults to today)."""
    today = on_date or date.today().isoformat()
    data = _load_streaks(snapshot_dir)
    dates = data.get(snapshot, [])
    if today not in dates:
        dates.append(today)
        dates.sort()
    data[snapshot] = dates
    _save_streaks(snapshot_dir, data)
    return StreakEntry(snapshot=snapshot, date=today)


def compute_streak(snapshot_dir: Path, snapshot: str) -> StreakReport:
    """Compute current and longest consecutive daily streaks for a snapshot."""
    data = _load_streaks(snapshot_dir)
    dates = sorted(data.get(snapshot, []))
    if not dates:
        return StreakReport(snapshot=snapshot)

    parsed = [date.fromisoformat(d) for d in dates]
    longest = current = 1
    for i in range(1, len(parsed)):
        if parsed[i] - parsed[i - 1] == timedelta(days=1):
            current += 1
            longest = max(longest, current)
        else:
            current = 1

    today = date.today()
    last = parsed[-1]
    if last < today - timedelta(days=1):
        current = 0
    else:
        current_streak = 1
        for i in range(len(parsed) - 1, 0, -1):
            if parsed[i] - parsed[i - 1] == timedelta(days=1):
                current_streak += 1
            else:
                break
        current = current_streak

    return StreakReport(
        snapshot=snapshot,
        dates=dates,
        current_streak=current,
        longest_streak=longest,
    )
