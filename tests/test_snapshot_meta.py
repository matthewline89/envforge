"""Tests for envforge.snapshot_meta."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_meta import (
    get_all_meta,
    get_meta,
    list_meta_snapshots,
    remove_meta,
    set_meta,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_set_meta_creates_meta_file(snapshot_dir: Path) -> None:
    set_meta(snapshot_dir, "snap1", "author", "alice")
    assert (snapshot_dir / "_meta.json").exists()


def test_set_meta_stores_value(snapshot_dir: Path) -> None:
    set_meta(snapshot_dir, "snap1", "author", "alice")
    assert get_meta(snapshot_dir, "snap1", "author") == "alice"


def test_set_meta_returns_true_when_new(snapshot_dir: Path) -> None:
    result = set_meta(snapshot_dir, "snap1", "env", "prod")
    assert result is True


def test_set_meta_returns_false_when_updated(snapshot_dir: Path) -> None:
    set_meta(snapshot_dir, "snap1", "env", "prod")
    result = set_meta(snapshot_dir, "snap1", "env", "staging")
    assert result is False


def test_set_meta_updates_value(snapshot_dir: Path) -> None:
    set_meta(snapshot_dir, "snap1", "env", "prod")
    set_meta(snapshot_dir, "snap1", "env", "staging")
    assert get_meta(snapshot_dir, "snap1", "env") == "staging"


def test_get_meta_returns_none_when_missing(snapshot_dir: Path) -> None:
    assert get_meta(snapshot_dir, "snap1", "missing") is None


def test_get_meta_returns_none_for_unknown_snapshot(snapshot_dir: Path) -> None:
    assert get_meta(snapshot_dir, "ghost", "key") is None


def test_remove_meta_returns_true_when_found(snapshot_dir: Path) -> None:
    set_meta(snapshot_dir, "snap1", "k", "v")
    assert remove_meta(snapshot_dir, "snap1", "k") is True


def test_remove_meta_returns_false_when_missing(snapshot_dir: Path) -> None:
    assert remove_meta(snapshot_dir, "snap1", "nope") is False


def test_remove_meta_deletes_key(snapshot_dir: Path) -> None:
    set_meta(snapshot_dir, "snap1", "k", "v")
    remove_meta(snapshot_dir, "snap1", "k")
    assert get_meta(snapshot_dir, "snap1", "k") is None


def test_remove_meta_removes_snapshot_entry_when_empty(snapshot_dir: Path) -> None:
    set_meta(snapshot_dir, "snap1", "k", "v")
    remove_meta(snapshot_dir, "snap1", "k")
    raw = json.loads((snapshot_dir / "_meta.json").read_text())
    assert "snap1" not in raw


def test_get_all_meta_returns_empty_dict(snapshot_dir: Path) -> None:
    assert get_all_meta(snapshot_dir, "snap1") == {}


def test_get_all_meta_returns_all_keys(snapshot_dir: Path) -> None:
    set_meta(snapshot_dir, "snap1", "a", "1")
    set_meta(snapshot_dir, "snap1", "b", "2")
    data = get_all_meta(snapshot_dir, "snap1")
    assert data == {"a": "1", "b": "2"}


def test_list_meta_snapshots_empty(snapshot_dir: Path) -> None:
    assert list_meta_snapshots(snapshot_dir) == []


def test_list_meta_snapshots_returns_names(snapshot_dir: Path) -> None:
    set_meta(snapshot_dir, "snap2", "x", "1")
    set_meta(snapshot_dir, "snap1", "y", "2")
    assert list_meta_snapshots(snapshot_dir) == ["snap1", "snap2"]
