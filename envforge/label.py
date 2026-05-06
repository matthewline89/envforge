"""Label management for snapshots — attach freeform labels and query by them."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _labels_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "labels.json"


def _load_labels(snapshot_dir: Path) -> Dict[str, List[str]]:
    path = _labels_path(snapshot_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_labels(snapshot_dir: Path, data: Dict[str, List[str]]) -> None:
    _labels_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def add_label(snapshot_dir: Path, snapshot_name: str, label: str) -> bool:
    """Attach *label* to *snapshot_name*. Returns True if the label was new."""
    data = _load_labels(snapshot_dir)
    labels = data.setdefault(snapshot_name, [])
    if label in labels:
        return False
    labels.append(label)
    _save_labels(snapshot_dir, data)
    return True


def remove_label(snapshot_dir: Path, snapshot_name: str, label: str) -> bool:
    """Remove *label* from *snapshot_name*. Returns True if it existed."""
    data = _load_labels(snapshot_dir)
    labels = data.get(snapshot_name, [])
    if label not in labels:
        return False
    labels.remove(label)
    data[snapshot_name] = labels
    _save_labels(snapshot_dir, data)
    return True


def get_labels(snapshot_dir: Path, snapshot_name: str) -> List[str]:
    """Return all labels attached to *snapshot_name*."""
    return _load_labels(snapshot_dir).get(snapshot_name, [])


def find_by_label(snapshot_dir: Path, label: str) -> List[str]:
    """Return snapshot names that carry *label*."""
    data = _load_labels(snapshot_dir)
    return [name for name, labels in data.items() if label in labels]


def list_labels(snapshot_dir: Path) -> Dict[str, List[str]]:
    """Return the full label mapping."""
    return _load_labels(snapshot_dir)


def clear_labels(snapshot_dir: Path, snapshot_name: str) -> int:
    """Remove all labels from *snapshot_name*. Returns number removed."""
    data = _load_labels(snapshot_dir)
    removed = len(data.pop(snapshot_name, []))
    if removed:
        _save_labels(snapshot_dir, data)
    return removed
