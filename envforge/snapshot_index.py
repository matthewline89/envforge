"""snapshot_index.py — build and query a searchable index of snapshot metadata."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envforge.snapshot import load, list_snapshots

_INDEX_FILE = "index.json"


@dataclass
class IndexEntry:
    name: str
    key_count: int
    keys: List[str]
    tags: List[str] = field(default_factory=list)


@dataclass
class SnapshotIndex:
    entries: Dict[str, IndexEntry] = field(default_factory=dict)


def _index_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _INDEX_FILE


def build_index(snapshot_dir: Path) -> SnapshotIndex:
    """Scan all snapshots in *snapshot_dir* and return a fresh SnapshotIndex."""
    index = SnapshotIndex()
    for name in list_snapshots(snapshot_dir):
        try:
            env = load(snapshot_dir, name)
        except Exception:
            continue
        index.entries[name] = IndexEntry(
            name=name,
            key_count=len(env),
            keys=sorted(env.keys()),
        )
    return index


def save_index(snapshot_dir: Path, index: SnapshotIndex) -> None:
    """Persist *index* to disk as JSON."""
    data = {
        name: {"key_count": e.key_count, "keys": e.keys, "tags": e.tags}
        for name, e in index.entries.items()
    }
    _index_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def load_index(snapshot_dir: Path) -> SnapshotIndex:
    """Load a previously saved index from disk."""
    path = _index_path(snapshot_dir)
    if not path.exists():
        return SnapshotIndex()
    raw = json.loads(path.read_text())
    entries = {
        name: IndexEntry(
            name=name,
            key_count=v["key_count"],
            keys=v["keys"],
            tags=v.get("tags", []),
        )
        for name, v in raw.items()
    }
    return SnapshotIndex(entries=entries)


def query_by_key(index: SnapshotIndex, key: str) -> List[IndexEntry]:
    """Return all entries whose key list contains *key* (exact match)."""
    return [e for e in index.entries.values() if key in e.keys]


def query_by_tag(index: SnapshotIndex, tag: str) -> List[IndexEntry]:
    """Return all entries that carry *tag*."""
    return [e for e in index.entries.values() if tag in e.tags]


def get_entry(index: SnapshotIndex, name: str) -> Optional[IndexEntry]:
    return index.entries.get(name)
