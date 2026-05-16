"""Snapshot caching — store and retrieve parsed snapshot data in memory."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional
import json
import time


@dataclass
class CacheEntry:
    name: str
    env: Dict[str, str]
    loaded_at: float
    ttl: float  # seconds; 0 means never expires

    @property
    def expired(self) -> bool:
        if self.ttl <= 0:
            return False
        return (time.monotonic() - self.loaded_at) > self.ttl


@dataclass
class SnapshotCache:
    _store: Dict[str, CacheEntry] = field(default_factory=dict)

    def put(self, name: str, env: Dict[str, str], ttl: float = 0.0) -> CacheEntry:
        entry = CacheEntry(name=name, env=dict(env), loaded_at=time.monotonic(), ttl=ttl)
        self._store[name] = entry
        return entry

    def get(self, name: str) -> Optional[CacheEntry]:
        entry = self._store.get(name)
        if entry is None:
            return None
        if entry.expired:
            del self._store[name]
            return None
        return entry

    def invalidate(self, name: str) -> bool:
        if name in self._store:
            del self._store[name]
            return True
        return False

    def clear(self) -> int:
        count = len(self._store)
        self._store.clear()
        return count

    def size(self) -> int:
        return len(self._store)

    def names(self) -> list[str]:
        return list(self._store.keys())


_default_cache: SnapshotCache = SnapshotCache()


def get_cache() -> SnapshotCache:
    return _default_cache


def load_cached(snapshot_dir: Path, name: str, ttl: float = 0.0) -> Dict[str, str]:
    """Return env dict from cache if present and valid, otherwise load from disk."""
    cache = get_cache()
    entry = cache.get(name)
    if entry is not None:
        return entry.env
    path = snapshot_dir / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found at {path}")
    env: Dict[str, str] = json.loads(path.read_text())
    cache.put(name, env, ttl=ttl)
    return env
