"""Tests for envforge.snapshot_index."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot import save
from envforge.snapshot_index import (
    IndexEntry,
    SnapshotIndex,
    build_index,
    get_entry,
    load_index,
    query_by_key,
    query_by_tag,
    save_index,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    snapshot_dir = tmp_path / "snapshots"
    snapshot_dir.mkdir()
    return snapshot_dir


def test_build_index_returns_snapshot_index(snapshot_dir):
    save(snapshot_dir, "alpha", {"FOO": "1"})
    result = build_index(snapshot_dir)
    assert isinstance(result, SnapshotIndex)


def test_build_index_includes_all_snapshots(snapshot_dir):
    save(snapshot_dir, "alpha", {"FOO": "1"})
    save(snapshot_dir, "beta", {"BAR": "2"})
    index = build_index(snapshot_dir)
    assert "alpha" in index.entries
    assert "beta" in index.entries


def test_build_index_records_key_count(snapshot_dir):
    save(snapshot_dir, "alpha", {"A": "1", "B": "2", "C": "3"})
    index = build_index(snapshot_dir)
    assert index.entries["alpha"].key_count == 3


def test_build_index_records_sorted_keys(snapshot_dir):
    save(snapshot_dir, "alpha", {"Z": "1", "A": "2"})
    index = build_index(snapshot_dir)
    assert index.entries["alpha"].keys == ["A", "Z"]


def test_save_and_load_index_roundtrip(snapshot_dir):
    save(snapshot_dir, "snap1", {"X": "10"})
    original = build_index(snapshot_dir)
    save_index(snapshot_dir, original)
    loaded = load_index(snapshot_dir)
    assert "snap1" in loaded.entries
    assert loaded.entries["snap1"].key_count == 1


def test_load_index_returns_empty_when_missing(snapshot_dir):
    index = load_index(snapshot_dir)
    assert index.entries == {}


def test_save_index_writes_json_file(snapshot_dir):
    save(snapshot_dir, "snap1", {"K": "v"})
    index = build_index(snapshot_dir)
    save_index(snapshot_dir, index)
    index_file = snapshot_dir / "index.json"
    assert index_file.exists()
    data = json.loads(index_file.read_text())
    assert "snap1" in data


def test_query_by_key_returns_matching_entries(snapshot_dir):
    save(snapshot_dir, "snap1", {"DATABASE_URL": "x"})
    save(snapshot_dir, "snap2", {"SECRET_KEY": "y"})
    index = build_index(snapshot_dir)
    results = query_by_key(index, "DATABASE_URL")
    assert len(results) == 1
    assert results[0].name == "snap1"


def test_query_by_key_returns_empty_when_no_match(snapshot_dir):
    save(snapshot_dir, "snap1", {"FOO": "1"})
    index = build_index(snapshot_dir)
    assert query_by_key(index, "MISSING_KEY") == []


def test_query_by_tag_returns_tagged_entries(snapshot_dir):
    save(snapshot_dir, "snap1", {"A": "1"})
    index = build_index(snapshot_dir)
    index.entries["snap1"].tags = ["production"]
    results = query_by_tag(index, "production")
    assert len(results) == 1
    assert results[0].name == "snap1"


def test_get_entry_returns_none_for_unknown(snapshot_dir):
    index = build_index(snapshot_dir)
    assert get_entry(index, "no-such-snap") is None


def test_get_entry_returns_entry_when_present(snapshot_dir):
    save(snapshot_dir, "mysnap", {"ENV": "prod"})
    index = build_index(snapshot_dir)
    entry = get_entry(index, "mysnap")
    assert isinstance(entry, IndexEntry)
    assert entry.name == "mysnap"
