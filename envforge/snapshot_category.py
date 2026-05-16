"""Categorize snapshots into user-defined categories."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


class CategoryError(Exception):
    pass


def _categories_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "categories.json"


def _load_categories(snapshot_dir: Path) -> Dict[str, List[str]]:
    path = _categories_path(snapshot_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_categories(snapshot_dir: Path, data: Dict[str, List[str]]) -> None:
    _categories_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def add_to_category(snapshot_dir: Path, category: str, snapshot_name: str) -> bool:
    """Add a snapshot to a category. Returns True if newly added, False if already present."""
    data = _load_categories(snapshot_dir)
    members = data.setdefault(category, [])
    if snapshot_name in members:
        return False
    members.append(snapshot_name)
    _save_categories(snapshot_dir, data)
    return True


def remove_from_category(snapshot_dir: Path, category: str, snapshot_name: str) -> bool:
    """Remove a snapshot from a category. Returns True if removed, False if not found."""
    data = _load_categories(snapshot_dir)
    members = data.get(category, [])
    if snapshot_name not in members:
        return False
    members.remove(snapshot_name)
    if not members:
        del data[category]
    _save_categories(snapshot_dir, data)
    return True


def list_categories(snapshot_dir: Path) -> List[str]:
    """Return all category names."""
    return sorted(_load_categories(snapshot_dir).keys())


def get_category_members(snapshot_dir: Path, category: str) -> List[str]:
    """Return all snapshot names in the given category."""
    return list(_load_categories(snapshot_dir).get(category, []))


def find_categories_for(snapshot_dir: Path, snapshot_name: str) -> List[str]:
    """Return all categories that contain the given snapshot."""
    data = _load_categories(snapshot_dir)
    return sorted(cat for cat, members in data.items() if snapshot_name in members)


def delete_category(snapshot_dir: Path, category: str) -> bool:
    """Delete an entire category. Returns True if it existed."""
    data = _load_categories(snapshot_dir)
    if category not in data:
        return False
    del data[category]
    _save_categories(snapshot_dir, data)
    return True
