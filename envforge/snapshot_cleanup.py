"""Snapshot cleanup: remove orphaned metadata files that reference missing snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envforge.snapshot import list_snapshots

_METADATA_FILES = [
    "tags.json",
    "aliases.json",
    "locks.json",
    "annotations.json",
    "labels.json",
    "notes.json",
    "bookmarks.json",
    "pins.json",
    "slots.json",
]


@dataclass
class CleanupResult:
    removed_snapshots: List[str] = field(default_factory=list)
    pruned_metadata_keys: List[str] = field(default_factory=list)


def total_removed(result: CleanupResult) -> int:
    return len(result.removed_snapshots) + len(result.pruned_metadata_keys)


def _load_json(path: Path) -> dict:
    import json
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _save_json(path: Path, data: dict) -> None:
    import json
    path.write_text(json.dumps(data, indent=2))


def cleanup_orphans(snapshot_dir: Path, dry_run: bool = False) -> CleanupResult:
    """Remove metadata entries that reference snapshots no longer on disk."""
    result = CleanupResult()
    existing = set(list_snapshots(snapshot_dir))

    for meta_filename in _METADATA_FILES:
        meta_path = snapshot_dir / meta_filename
        if not meta_path.exists():
            continue
        data = _load_json(meta_path)
        orphaned = [k for k in data if k not in existing]
        if not orphaned:
            continue
        for key in orphaned:
            result.pruned_metadata_keys.append(f"{meta_filename}::{key}")
        if not dry_run:
            for key in orphaned:
                del data[key]
            _save_json(meta_path, data)

    return result
