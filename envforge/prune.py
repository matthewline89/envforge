"""Prune old or unused snapshots based on age or count limits."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


@dataclass
class PruneResult:
    removed: List[str] = field(default_factory=list)
    kept: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def total_removed(self) -> int:
        return len(self.removed)


def _snapshot_mtime(path: Path) -> datetime:
    """Return the modification time of a snapshot file as an aware UTC datetime."""
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def _snapshot_names(snapshot_dir: Path) -> List[Path]:
    """Return all snapshot JSON files sorted oldest-first by mtime."""
    files = sorted(snapshot_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
    # Exclude metadata files used by other modules
    excluded = {"tags.json", "aliases.json", "pins.json", "history.json", "audit.json"}
    return [f for f in files if f.name not in excluded]


def prune_by_count(
    snapshot_dir: Path,
    keep: int,
) -> PruneResult:
    """Remove oldest snapshots, keeping only the *keep* most recent."""
    if keep < 1:
        raise ValueError("keep must be >= 1")

    result = PruneResult()
    snapshots = _snapshot_names(snapshot_dir)

    to_remove = snapshots[: max(0, len(snapshots) - keep)]
    to_keep = snapshots[max(0, len(snapshots) - keep) :]

    for path in to_keep:
        result.kept.append(path.stem)

    for path in to_remove:
        try:
            path.unlink()
            result.removed.append(path.stem)
        except OSError as exc:  # pragma: no cover
            result.errors.append(f"{path.stem}: {exc}")

    return result


def prune_by_age(
    snapshot_dir: Path,
    max_age_days: float,
    now: Optional[datetime] = None,
) -> PruneResult:
    """Remove snapshots older than *max_age_days* days."""
    if max_age_days <= 0:
        raise ValueError("max_age_days must be > 0")

    if now is None:
        now = datetime.now(tz=timezone.utc)

    result = PruneResult()
    for path in _snapshot_names(snapshot_dir):
        age = (now - _snapshot_mtime(path)).total_seconds() / 86400
        if age > max_age_days:
            try:
                path.unlink()
                result.removed.append(path.stem)
            except OSError as exc:  # pragma: no cover
                result.errors.append(f"{path.stem}: {exc}")
        else:
            result.kept.append(path.stem)

    return result
