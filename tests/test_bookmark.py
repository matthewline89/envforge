"""Tests for envforge.bookmark."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.bookmark import (
    list_bookmarks,
    remove_bookmark,
    resolve_bookmark,
    set_bookmark,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_set_bookmark_creates_bookmarks_file(snapshot_dir: Path) -> None:
    set_bookmark(snapshot_dir, "prod", "production-2024")
    assert (snapshot_dir / "bookmarks.json").exists()


def test_set_bookmark_stores_mapping(snapshot_dir: Path) -> None:
    set_bookmark(snapshot_dir, "prod", "production-2024")
    data = json.loads((snapshot_dir / "bookmarks.json").read_text())
    assert data["prod"] == "production-2024"


def test_set_bookmark_returns_true_when_new(snapshot_dir: Path) -> None:
    result = set_bookmark(snapshot_dir, "dev", "dev-snapshot")
    assert result is True


def test_set_bookmark_returns_false_when_overwritten(snapshot_dir: Path) -> None:
    set_bookmark(snapshot_dir, "dev", "dev-snapshot-v1")
    result = set_bookmark(snapshot_dir, "dev", "dev-snapshot-v2")
    assert result is False


def test_set_bookmark_overwrites_existing(snapshot_dir: Path) -> None:
    set_bookmark(snapshot_dir, "dev", "dev-snapshot-v1")
    set_bookmark(snapshot_dir, "dev", "dev-snapshot-v2")
    assert resolve_bookmark(snapshot_dir, "dev") == "dev-snapshot-v2"


def test_remove_bookmark_returns_true_when_found(snapshot_dir: Path) -> None:
    set_bookmark(snapshot_dir, "staging", "staging-snap")
    assert remove_bookmark(snapshot_dir, "staging") is True


def test_remove_bookmark_returns_false_when_missing(snapshot_dir: Path) -> None:
    assert remove_bookmark(snapshot_dir, "nonexistent") is False


def test_remove_bookmark_deletes_entry(snapshot_dir: Path) -> None:
    set_bookmark(snapshot_dir, "staging", "staging-snap")
    remove_bookmark(snapshot_dir, "staging")
    assert resolve_bookmark(snapshot_dir, "staging") is None


def test_resolve_bookmark_returns_name(snapshot_dir: Path) -> None:
    set_bookmark(snapshot_dir, "latest", "env-20240101")
    assert resolve_bookmark(snapshot_dir, "latest") == "env-20240101"


def test_resolve_bookmark_returns_none_for_missing(snapshot_dir: Path) -> None:
    assert resolve_bookmark(snapshot_dir, "ghost") is None


def test_list_bookmarks_returns_empty_dict(snapshot_dir: Path) -> None:
    assert list_bookmarks(snapshot_dir) == {}


def test_list_bookmarks_returns_all_entries(snapshot_dir: Path) -> None:
    set_bookmark(snapshot_dir, "a", "snap-a")
    set_bookmark(snapshot_dir, "b", "snap-b")
    result = list_bookmarks(snapshot_dir)
    assert result == {"a": "snap-a", "b": "snap-b"}
