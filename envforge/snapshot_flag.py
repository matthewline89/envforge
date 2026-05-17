"""Snapshot flag management — set, remove, and query boolean flags on snapshots."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


class FlagError(Exception):
    pass


def _flags_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "flags.json"


def _load_flags(snapshot_dir: Path) -> Dict[str, List[str]]:
    p = _flags_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_flags(snapshot_dir: Path, data: Dict[str, List[str]]) -> None:
    _flags_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def set_flag(snapshot_dir: Path, name: str, flag: str) -> bool:
    """Add *flag* to *name*. Returns True when newly added, False if already present."""
    data = _load_flags(snapshot_dir)
    flags = data.setdefault(name, [])
    if flag in flags:
        return False
    flags.append(flag)
    _save_flags(snapshot_dir, data)
    return True


def remove_flag(snapshot_dir: Path, name: str, flag: str) -> bool:
    """Remove *flag* from *name*. Returns True when removed, False if not found."""
    data = _load_flags(snapshot_dir)
    flags = data.get(name, [])
    if flag not in flags:
        return False
    flags.remove(flag)
    data[name] = flags
    _save_flags(snapshot_dir, data)
    return True


def get_flags(snapshot_dir: Path, name: str) -> List[str]:
    """Return all flags set on *name*."""
    return list(_load_flags(snapshot_dir).get(name, []))


def has_flag(snapshot_dir: Path, name: str, flag: str) -> bool:
    """Return True if *name* has *flag* set."""
    return flag in _load_flags(snapshot_dir).get(name, [])


def find_by_flag(snapshot_dir: Path, flag: str) -> List[str]:
    """Return all snapshot names that carry *flag*."""
    data = _load_flags(snapshot_dir)
    return [name for name, flags in data.items() if flag in flags]


def clear_flags(snapshot_dir: Path, name: str) -> int:
    """Remove all flags from *name*. Returns the number of flags cleared."""
    data = _load_flags(snapshot_dir)
    count = len(data.pop(name, []))
    _save_flags(snapshot_dir, data)
    return count
