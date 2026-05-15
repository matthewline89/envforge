"""Snapshot rating — let users rate snapshots from 1–5 stars."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class RatingError(Exception):
    pass


def _ratings_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "ratings.json"


def _load_ratings(snapshot_dir: Path) -> dict[str, int]:
    p = _ratings_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ratings(snapshot_dir: Path, data: dict[str, int]) -> None:
    _ratings_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def set_rating(snapshot_dir: Path, name: str, stars: int) -> bool:
    """Rate a snapshot 1–5 stars. Returns True if new, False if updated."""
    if not (1 <= stars <= 5):
        raise RatingError(f"Rating must be between 1 and 5, got {stars}")
    data = _load_ratings(snapshot_dir)
    is_new = name not in data
    data[name] = stars
    _save_ratings(snapshot_dir, data)
    return is_new


def remove_rating(snapshot_dir: Path, name: str) -> bool:
    """Remove a rating. Returns True if it existed."""
    data = _load_ratings(snapshot_dir)
    if name not in data:
        return False
    del data[name]
    _save_ratings(snapshot_dir, data)
    return True


def get_rating(snapshot_dir: Path, name: str) -> Optional[int]:
    """Return the star rating for a snapshot, or None."""
    return _load_ratings(snapshot_dir).get(name)


def list_ratings(snapshot_dir: Path) -> dict[str, int]:
    """Return all snapshot ratings."""
    return _load_ratings(snapshot_dir)


@dataclass
class TopRated:
    name: str
    stars: int


def top_rated(snapshot_dir: Path, limit: int = 5) -> list[TopRated]:
    """Return the top-rated snapshots, sorted by stars descending."""
    data = _load_ratings(snapshot_dir)
    ranked = sorted(data.items(), key=lambda kv: kv[1], reverse=True)
    return [TopRated(name=k, stars=v) for k, v in ranked[:limit]]
