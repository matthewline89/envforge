"""Manage favorite (starred) snapshots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

_FAVORITES_FILE = "favorites.json"


def _favorites_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _FAVORITES_FILE


def _load_favorites(snapshot_dir: Path) -> List[str]:
    path = _favorites_path(snapshot_dir)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_favorites(snapshot_dir: Path, favorites: List[str]) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    _favorites_path(snapshot_dir).write_text(json.dumps(favorites, indent=2))


def add_favorite(snapshot_dir: Path, name: str) -> bool:
    """Star a snapshot. Returns True if newly added, False if already starred."""
    favorites = _load_favorites(snapshot_dir)
    if name in favorites:
        return False
    favorites.append(name)
    _save_favorites(snapshot_dir, favorites)
    return True


def remove_favorite(snapshot_dir: Path, name: str) -> bool:
    """Unstar a snapshot. Returns True if removed, False if not found."""
    favorites = _load_favorites(snapshot_dir)
    if name not in favorites:
        return False
    favorites.remove(name)
    _save_favorites(snapshot_dir, favorites)
    return True


def list_favorites(snapshot_dir: Path) -> List[str]:
    """Return all starred snapshot names."""
    return list(_load_favorites(snapshot_dir))


def is_favorite(snapshot_dir: Path, name: str) -> bool:
    """Return True if the snapshot is starred."""
    return name in _load_favorites(snapshot_dir)
