"""Tests for envforge.lock."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge import lock as lock_mod


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_lock_snapshot_creates_locks_file(snapshot_dir: Path) -> None:
    lock_mod.lock_snapshot(snapshot_dir, "snap1")
    assert (snapshot_dir / "locks.json").exists()


def test_lock_snapshot_stores_name(snapshot_dir: Path) -> None:
    lock_mod.lock_snapshot(snapshot_dir, "snap1")
    data = json.loads((snapshot_dir / "locks.json").read_text())
    assert "snap1" in data


def test_lock_snapshot_returns_true_when_new(snapshot_dir: Path) -> None:
    result = lock_mod.lock_snapshot(snapshot_dir, "snap1")
    assert result is True


def test_lock_snapshot_returns_false_when_already_locked(snapshot_dir: Path) -> None:
    lock_mod.lock_snapshot(snapshot_dir, "snap1")
    result = lock_mod.lock_snapshot(snapshot_dir, "snap1")
    assert result is False


def test_unlock_snapshot_returns_true_when_found(snapshot_dir: Path) -> None:
    lock_mod.lock_snapshot(snapshot_dir, "snap1")
    result = lock_mod.unlock_snapshot(snapshot_dir, "snap1")
    assert result is True


def test_unlock_snapshot_removes_name(snapshot_dir: Path) -> None:
    lock_mod.lock_snapshot(snapshot_dir, "snap1")
    lock_mod.unlock_snapshot(snapshot_dir, "snap1")
    assert not lock_mod.is_locked(snapshot_dir, "snap1")


def test_unlock_snapshot_returns_false_when_not_locked(snapshot_dir: Path) -> None:
    result = lock_mod.unlock_snapshot(snapshot_dir, "snap1")
    assert result is False


def test_is_locked_true_after_lock(snapshot_dir: Path) -> None:
    lock_mod.lock_snapshot(snapshot_dir, "snap1")
    assert lock_mod.is_locked(snapshot_dir, "snap1") is True


def test_is_locked_false_before_lock(snapshot_dir: Path) -> None:
    assert lock_mod.is_locked(snapshot_dir, "snap1") is False


def test_list_locks_returns_all_locked(snapshot_dir: Path) -> None:
    lock_mod.lock_snapshot(snapshot_dir, "a")
    lock_mod.lock_snapshot(snapshot_dir, "b")
    locks = lock_mod.list_locks(snapshot_dir)
    assert set(locks) == {"a", "b"}


def test_list_locks_empty_when_none(snapshot_dir: Path) -> None:
    assert lock_mod.list_locks(snapshot_dir) == []


def test_multiple_snapshots_can_be_locked_independently(snapshot_dir: Path) -> None:
    lock_mod.lock_snapshot(snapshot_dir, "snap1")
    lock_mod.lock_snapshot(snapshot_dir, "snap2")
    lock_mod.unlock_snapshot(snapshot_dir, "snap1")
    assert not lock_mod.is_locked(snapshot_dir, "snap1")
    assert lock_mod.is_locked(snapshot_dir, "snap2")
