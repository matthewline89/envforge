"""Attach and retrieve arbitrary metadata for snapshots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MetaError(Exception):
    pass


def _meta_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "_meta.json"


def _load_meta(snapshot_dir: Path) -> dict[str, dict[str, Any]]:
    p = _meta_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_meta(snapshot_dir: Path, data: dict[str, dict[str, Any]]) -> None:
    _meta_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def set_meta(snapshot_dir: Path, name: str, key: str, value: Any) -> bool:
    """Set a metadata key for a snapshot. Returns True if the key is new."""
    data = _load_meta(snapshot_dir)
    entry = data.setdefault(name, {})
    is_new = key not in entry
    entry[key] = value
    _save_meta(snapshot_dir, data)
    return is_new


def get_meta(snapshot_dir: Path, name: str, key: str) -> Any | None:
    """Return the metadata value for a key, or None if not found."""
    data = _load_meta(snapshot_dir)
    return data.get(name, {}).get(key)


def remove_meta(snapshot_dir: Path, name: str, key: str) -> bool:
    """Remove a metadata key. Returns True if it existed."""
    data = _load_meta(snapshot_dir)
    entry = data.get(name, {})
    if key not in entry:
        return False
    del entry[key]
    if not entry:
        data.pop(name, None)
    _save_meta(snapshot_dir, data)
    return True


def get_all_meta(snapshot_dir: Path, name: str) -> dict[str, Any]:
    """Return all metadata for a snapshot (empty dict if none)."""
    return dict(_load_meta(snapshot_dir).get(name, {}))


def list_meta_snapshots(snapshot_dir: Path) -> list[str]:
    """Return snapshot names that have any metadata."""
    return sorted(_load_meta(snapshot_dir).keys())
