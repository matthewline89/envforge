"""Tests for envforge.snapshot_access."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_access import (
    AccessEntry,
    _access_path,
    get_access,
    list_access,
    record_access,
    reset_access,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_record_access_creates_access_file(snapshot_dir: Path) -> None:
    record_access(snapshot_dir, "env-a")
    assert _access_path(snapshot_dir).exists()


def test_record_access_returns_access_entry(snapshot_dir: Path) -> None:
    entry = record_access(snapshot_dir, "env-a")
    assert isinstance(entry, AccessEntry)
    assert entry.name == "env-a"


def test_record_access_increments_count(snapshot_dir: Path) -> None:
    record_access(snapshot_dir, "env-a")
    entry = record_access(snapshot_dir, "env-a")
    assert entry.access_count == 2


def test_record_access_starts_at_one(snapshot_dir: Path) -> None:
    entry = record_access(snapshot_dir, "env-b")
    assert entry.access_count == 1


def test_record_access_stores_iso_timestamp(snapshot_dir: Path) -> None:
    entry = record_access(snapshot_dir, "env-a")
    # ISO-8601 timestamps contain a 'T'
    assert "T" in entry.last_accessed


def test_get_access_returns_none_for_unknown(snapshot_dir: Path) -> None:
    result = get_access(snapshot_dir, "ghost")
    assert result is None


def test_get_access_returns_entry_after_record(snapshot_dir: Path) -> None:
    record_access(snapshot_dir, "env-c")
    entry = get_access(snapshot_dir, "env-c")
    assert entry is not None
    assert entry.name == "env-c"
    assert entry.access_count == 1


def test_list_access_returns_all_entries(snapshot_dir: Path) -> None:
    record_access(snapshot_dir, "alpha")
    record_access(snapshot_dir, "beta")
    entries = list_access(snapshot_dir)
    names = {e.name for e in entries}
    assert "alpha" in names
    assert "beta" in names


def test_list_access_sorted_most_recent_first(snapshot_dir: Path) -> None:
    record_access(snapshot_dir, "old")
    record_access(snapshot_dir, "new")
    entries = list_access(snapshot_dir)
    # 'new' was accessed last so its timestamp is larger
    assert entries[0].name == "new"


def test_reset_access_returns_true_when_found(snapshot_dir: Path) -> None:
    record_access(snapshot_dir, "env-d")
    assert reset_access(snapshot_dir, "env-d") is True


def test_reset_access_returns_false_when_missing(snapshot_dir: Path) -> None:
    assert reset_access(snapshot_dir, "no-such") is False


def test_reset_access_removes_entry(snapshot_dir: Path) -> None:
    record_access(snapshot_dir, "env-e")
    reset_access(snapshot_dir, "env-e")
    assert get_access(snapshot_dir, "env-e") is None
