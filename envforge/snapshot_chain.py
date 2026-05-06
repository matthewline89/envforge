"""Snapshot chaining: link snapshots into an ordered chain with parent references."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


_CHAINS_FILE = "chains.json"


@dataclass
class ChainError(Exception):
    message: str

    def __str__(self) -> str:
        return self.message


@dataclass
class ChainEntry:
    name: str
    parent: Optional[str]


@dataclass
class Chain:
    entries: List[ChainEntry] = field(default_factory=list)

    def ordered_names(self) -> List[str]:
        """Return snapshot names in chain order (root first)."""
        return [e.name for e in self.entries]


def _chains_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _CHAINS_FILE


def _load_chains(snapshot_dir: Path) -> dict:
    p = _chains_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_chains(snapshot_dir: Path, data: dict) -> None:
    _chains_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def link_snapshot(snapshot_dir: Path, name: str, parent: Optional[str]) -> bool:
    """Link *name* to *parent*. Returns True if newly added, False if updated."""
    data = _load_chains(snapshot_dir)
    is_new = name not in data
    data[name] = parent
    _save_chains(snapshot_dir, data)
    return is_new


def unlink_snapshot(snapshot_dir: Path, name: str) -> bool:
    """Remove *name* from chain records. Returns True if it existed."""
    data = _load_chains(snapshot_dir)
    if name not in data:
        return False
    del data[name]
    _save_chains(snapshot_dir, data)
    return True


def get_chain(snapshot_dir: Path, name: str) -> Chain:
    """Walk parent references from *name* back to the root and return ordered Chain."""
    data = _load_chains(snapshot_dir)
    if name not in data:
        raise ChainError(f"Snapshot '{name}' is not part of any chain.")
    entries: List[ChainEntry] = []
    visited = set()
    current: Optional[str] = name
    while current is not None:
        if current in visited:
            raise ChainError(f"Cycle detected in chain at '{current}'.")
        visited.add(current)
        parent = data.get(current)
        entries.append(ChainEntry(name=current, parent=parent))
        current = parent
    entries.reverse()
    return Chain(entries=entries)


def list_chains(snapshot_dir: Path) -> dict:
    """Return raw mapping of snapshot -> parent."""
    return _load_chains(snapshot_dir)
