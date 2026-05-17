"""Tests for envforge.snapshot_flag."""
from __future__ import annotations

from pathlib import Path

import pytest

from envforge.snapshot_flag import (
    clear_flags,
    find_by_flag,
    get_flags,
    has_flag,
    remove_flag,
    set_flag,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_set_flag_creates_flags_file(snapshot_dir: Path) -> None:
    set_flag(snapshot_dir, "snap1", "important")
    assert (snapshot_dir / "flags.json").exists()


def test_set_flag_returns_true_when_new(snapshot_dir: Path) -> None:
    assert set_flag(snapshot_dir, "snap1", "important") is True


def test_set_flag_returns_false_when_already_set(snapshot_dir: Path) -> None:
    set_flag(snapshot_dir, "snap1", "important")
    assert set_flag(snapshot_dir, "snap1", "important") is False


def test_set_flag_stores_flag(snapshot_dir: Path) -> None:
    set_flag(snapshot_dir, "snap1", "reviewed")
    assert "reviewed" in get_flags(snapshot_dir, "snap1")


def test_set_flag_allows_multiple_flags(snapshot_dir: Path) -> None:
    set_flag(snapshot_dir, "snap1", "reviewed")
    set_flag(snapshot_dir, "snap1", "stable")
    flags = get_flags(snapshot_dir, "snap1")
    assert "reviewed" in flags
    assert "stable" in flags


def test_remove_flag_returns_true_when_found(snapshot_dir: Path) -> None:
    set_flag(snapshot_dir, "snap1", "temp")
    assert remove_flag(snapshot_dir, "snap1", "temp") is True


def test_remove_flag_returns_false_when_not_found(snapshot_dir: Path) -> None:
    assert remove_flag(snapshot_dir, "snap1", "ghost") is False


def test_remove_flag_deletes_flag(snapshot_dir: Path) -> None:
    set_flag(snapshot_dir, "snap1", "temp")
    remove_flag(snapshot_dir, "snap1", "temp")
    assert "temp" not in get_flags(snapshot_dir, "snap1")


def test_has_flag_returns_true_when_set(snapshot_dir: Path) -> None:
    set_flag(snapshot_dir, "snap1", "pinned")
    assert has_flag(snapshot_dir, "snap1", "pinned") is True


def test_has_flag_returns_false_when_not_set(snapshot_dir: Path) -> None:
    assert has_flag(snapshot_dir, "snap1", "pinned") is False


def test_find_by_flag_returns_matching_snapshots(snapshot_dir: Path) -> None:
    set_flag(snapshot_dir, "snap1", "reviewed")
    set_flag(snapshot_dir, "snap2", "reviewed")
    set_flag(snapshot_dir, "snap3", "other")
    result = find_by_flag(snapshot_dir, "reviewed")
    assert "snap1" in result
    assert "snap2" in result
    assert "snap3" not in result


def test_find_by_flag_returns_empty_when_no_match(snapshot_dir: Path) -> None:
    assert find_by_flag(snapshot_dir, "nonexistent") == []


def test_clear_flags_returns_count(snapshot_dir: Path) -> None:
    set_flag(snapshot_dir, "snap1", "a")
    set_flag(snapshot_dir, "snap1", "b")
    assert clear_flags(snapshot_dir, "snap1") == 2


def test_clear_flags_removes_all(snapshot_dir: Path) -> None:
    set_flag(snapshot_dir, "snap1", "a")
    set_flag(snapshot_dir, "snap1", "b")
    clear_flags(snapshot_dir, "snap1")
    assert get_flags(snapshot_dir, "snap1") == []


def test_get_flags_returns_empty_for_unknown(snapshot_dir: Path) -> None:
    assert get_flags(snapshot_dir, "nobody") == []
