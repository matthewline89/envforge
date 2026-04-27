"""Tag management for envforge snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

TAGS_FILE = "tags.json"


def _load_tags(snapshot_dir: Path) -> Dict[str, str]:
    """Load the tags mapping (tag -> snapshot name) from disk."""
    tags_path = snapshot_dir / TAGS_FILE
    if not tags_path.exists():
        return {}
    with tags_path.open("r") as f:
        return json.load(f)


def _save_tags(snapshot_dir: Path, tags: Dict[str, str]) -> None:
    """Persist the tags mapping to disk."""
    tags_path = snapshot_dir / TAGS_FILE
    with tags_path.open("w") as f:
        json.dump(tags, f, indent=2)


def add_tag(snapshot_dir: Path, tag: str, snapshot_name: str) -> None:
    """Associate *tag* with *snapshot_name*, overwriting any previous mapping."""
    tags = _load_tags(snapshot_dir)
    tags[tag] = snapshot_name
    _save_tags(snapshot_dir, tags)


def remove_tag(snapshot_dir: Path, tag: str) -> bool:
    """Remove *tag*. Returns True if the tag existed, False otherwise."""
    tags = _load_tags(snapshot_dir)
    if tag not in tags:
        return False
    del tags[tag]
    _save_tags(snapshot_dir, tags)
    return True


def resolve_tag(snapshot_dir: Path, tag: str) -> Optional[str]:
    """Return the snapshot name for *tag*, or None if not found."""
    return _load_tags(snapshot_dir).get(tag)


def list_tags(snapshot_dir: Path) -> Dict[str, str]:
    """Return all tag -> snapshot_name mappings."""
    return _load_tags(snapshot_dir)


def tags_for_snapshot(snapshot_dir: Path, snapshot_name: str) -> List[str]:
    """Return every tag that points to *snapshot_name*."""
    return [
        tag
        for tag, name in _load_tags(snapshot_dir).items()
        if name == snapshot_name
    ]
