"""Lock snapshots to prevent accidental modification or deletion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

_LOCKS_FILE = "locks.json"


def _locks_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _LOCKS_FILE


def _load_locks(snapshot_dir: Path) -> List[str]:
    path = _locks_path(snapshot_dir)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_locks(snapshot_dir: Path, locks: List[str]) -> None:
    _locks_path(snapshot_dir).write_text(json.dumps(locks, indent=2))


def lock_snapshot(snapshot_dir: Path, name: str) -> bool:
    """Lock a snapshot. Returns True if newly locked, False if already locked."""
    locks = _load_locks(snapshot_dir)
    if name in locks:
        return False
    locks.append(name)
    _save_locks(snapshot_dir, locks)
    return True


def unlock_snapshot(snapshot_dir: Path, name: str) -> bool:
    """Unlock a snapshot. Returns True if found and removed, False otherwise."""
    locks = _load_locks(snapshot_dir)
    if name not in locks:
        return False
    locks.remove(name)
    _save_locks(snapshot_dir, locks)
    return True


def is_locked(snapshot_dir: Path, name: str) -> bool:
    """Return True if the snapshot is currently locked."""
    return name in _load_locks(snapshot_dir)


def list_locks(snapshot_dir: Path) -> List[str]:
    """Return all currently locked snapshot names."""
    return list(_load_locks(snapshot_dir))
