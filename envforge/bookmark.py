"""Bookmark management: assign friendly bookmarks to snapshot names."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

_BOOKMARKS_FILE = "bookmarks.json"


def _bookmarks_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _BOOKMARKS_FILE


def _load_bookmarks(snapshot_dir: Path) -> dict[str, str]:
    path = _bookmarks_path(snapshot_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_bookmarks(snapshot_dir: Path, bookmarks: dict[str, str]) -> None:
    _bookmarks_path(snapshot_dir).write_text(json.dumps(bookmarks, indent=2))


def set_bookmark(snapshot_dir: Path, bookmark: str, snapshot_name: str) -> bool:
    """Create or update a bookmark. Returns True if new, False if overwritten."""
    bookmarks = _load_bookmarks(snapshot_dir)
    is_new = bookmark not in bookmarks
    bookmarks[bookmark] = snapshot_name
    _save_bookmarks(snapshot_dir, bookmarks)
    return is_new


def remove_bookmark(snapshot_dir: Path, bookmark: str) -> bool:
    """Remove a bookmark. Returns True if found and removed, False otherwise."""
    bookmarks = _load_bookmarks(snapshot_dir)
    if bookmark not in bookmarks:
        return False
    del bookmarks[bookmark]
    _save_bookmarks(snapshot_dir, bookmarks)
    return True


def resolve_bookmark(snapshot_dir: Path, bookmark: str) -> Optional[str]:
    """Return the snapshot name for a bookmark, or None if not found."""
    return _load_bookmarks(snapshot_dir).get(bookmark)


def list_bookmarks(snapshot_dir: Path) -> dict[str, str]:
    """Return all bookmarks as a mapping of bookmark -> snapshot name."""
    return _load_bookmarks(snapshot_dir)
