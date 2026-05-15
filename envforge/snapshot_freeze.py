"""Freeze and unfreeze snapshots to prevent modification."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


def _freeze_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "_freeze.json"


def _load_frozen(snapshot_dir: Path) -> List[str]:
    p = _freeze_path(snapshot_dir)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_frozen(snapshot_dir: Path, names: List[str]) -> None:
    _freeze_path(snapshot_dir).write_text(json.dumps(sorted(set(names)), indent=2))


@dataclass
class FreezeResult:
    name: str
    frozen: bool  # True = newly frozen, False = already frozen


def freeze_snapshot(snapshot_dir: Path, name: str) -> FreezeResult:
    """Mark a snapshot as frozen. Returns FreezeResult."""
    names = _load_frozen(snapshot_dir)
    if name in names:
        return FreezeResult(name=name, frozen=False)
    names.append(name)
    _save_frozen(snapshot_dir, names)
    return FreezeResult(name=name, frozen=True)


def unfreeze_snapshot(snapshot_dir: Path, name: str) -> bool:
    """Remove freeze from a snapshot. Returns True if it was frozen."""
    names = _load_frozen(snapshot_dir)
    if name not in names:
        return False
    names.remove(name)
    _save_frozen(snapshot_dir, names)
    return True


def is_frozen(snapshot_dir: Path, name: str) -> bool:
    """Return True if the snapshot is currently frozen."""
    return name in _load_frozen(snapshot_dir)


def list_frozen(snapshot_dir: Path) -> List[str]:
    """Return all frozen snapshot names."""
    return _load_frozen(snapshot_dir)
