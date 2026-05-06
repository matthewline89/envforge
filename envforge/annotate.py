"""Snapshot annotation support — attach and retrieve freeform notes on snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class AnnotationError(Exception):
    pass


def _annotations_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "annotations.json"


def _load_annotations(snapshot_dir: Path) -> dict[str, str]:
    path = _annotations_path(snapshot_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_annotations(snapshot_dir: Path, data: dict[str, str]) -> None:
    _annotations_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def set_annotation(snapshot_dir: Path, name: str, note: str) -> None:
    """Attach a freeform note to *name*."""
    data = _load_annotations(snapshot_dir)
    data[name] = note
    _save_annotations(snapshot_dir, data)


def remove_annotation(snapshot_dir: Path, name: str) -> bool:
    """Remove the annotation for *name*. Returns True if it existed."""
    data = _load_annotations(snapshot_dir)
    if name not in data:
        return False
    del data[name]
    _save_annotations(snapshot_dir, data)
    return True


def get_annotation(snapshot_dir: Path, name: str) -> Optional[str]:
    """Return the annotation for *name*, or None if absent."""
    return _load_annotations(snapshot_dir).get(name)


def list_annotations(snapshot_dir: Path) -> dict[str, str]:
    """Return all annotations keyed by snapshot name."""
    return dict(_load_annotations(snapshot_dir))
