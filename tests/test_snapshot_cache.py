"""Tests for envforge.snapshot_cache."""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from envforge.snapshot_cache import (
    CacheEntry,
    SnapshotCache,
    load_cached,
    get_cache,
)


@pytest.fixture(autouse=True)
def clear_default_cache():
    get_cache().clear()
    yield
    get_cache().clear()


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


def test_put_returns_cache_entry():
    cache = SnapshotCache()
    entry = cache.put("dev", {"A": "1"})
    assert isinstance(entry, CacheEntry)
    assert entry.name == "dev"
    assert entry.env == {"A": "1"}


def test_get_returns_entry_after_put():
    cache = SnapshotCache()
    cache.put("dev", {"A": "1"})
    result = cache.get("dev")
    assert result is not None
    assert result.env == {"A": "1"}


def test_get_returns_none_for_missing():
    cache = SnapshotCache()
    assert cache.get("nope") is None


def test_expired_entry_returns_none(monkeypatch):
    cache = SnapshotCache()
    start = time.monotonic()
    monkeypatch.setattr("envforge.snapshot_cache.time.monotonic", lambda: start)
    cache.put("dev", {"A": "1"}, ttl=5.0)
    # advance time beyond ttl
    monkeypatch.setattr("envforge.snapshot_cache.time.monotonic", lambda: start + 10.0)
    assert cache.get("dev") is None


def test_zero_ttl_never_expires(monkeypatch):
    cache = SnapshotCache()
    start = time.monotonic()
    monkeypatch.setattr("envforge.snapshot_cache.time.monotonic", lambda: start)
    cache.put("dev", {"A": "1"}, ttl=0.0)
    monkeypatch.setattr("envforge.snapshot_cache.time.monotonic", lambda: start + 9999.0)
    assert cache.get("dev") is not None


def test_invalidate_removes_entry():
    cache = SnapshotCache()
    cache.put("dev", {})
    assert cache.invalidate("dev") is True
    assert cache.get("dev") is None


def test_invalidate_returns_false_when_missing():
    cache = SnapshotCache()
    assert cache.invalidate("ghost") is False


def test_clear_removes_all_entries():
    cache = SnapshotCache()
    cache.put("a", {})
    cache.put("b", {})
    removed = cache.clear()
    assert removed == 2
    assert cache.size() == 0


def test_names_lists_cached_snapshots():
    cache = SnapshotCache()
    cache.put("x", {})
    cache.put("y", {})
    assert set(cache.names()) == {"x", "y"}


def test_load_cached_reads_from_disk(snapshot_dir):
    _write(snapshot_dir, "prod", {"DB": "localhost"})
    env = load_cached(snapshot_dir, "prod")
    assert env["DB"] == "localhost"


def test_load_cached_populates_cache(snapshot_dir):
    _write(snapshot_dir, "prod", {"DB": "localhost"})
    load_cached(snapshot_dir, "prod")
    assert get_cache().get("prod") is not None


def test_load_cached_raises_for_missing(snapshot_dir):
    with pytest.raises(FileNotFoundError):
        load_cached(snapshot_dir, "missing")
