"""Tests for envforge.snapshot_set."""

from __future__ import annotations

import pytest
from pathlib import Path

from envforge.snapshot_set import (
    create_set,
    delete_set,
    get_set,
    list_sets,
    add_to_set,
    remove_from_set,
    SnapshotSetError,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_create_set_creates_file(snapshot_dir):
    create_set(snapshot_dir, "myset", ["snap1", "snap2"])
    assert (snapshot_dir / "_snapshot_sets.json").exists()


def test_create_set_returns_true_when_new(snapshot_dir):
    assert create_set(snapshot_dir, "myset", ["snap1"]) is True


def test_create_set_returns_false_when_overwritten(snapshot_dir):
    create_set(snapshot_dir, "myset", ["snap1"])
    assert create_set(snapshot_dir, "myset", ["snap2"]) is False


def test_create_set_deduplicates_members(snapshot_dir):
    create_set(snapshot_dir, "myset", ["a", "b", "a"])
    assert get_set(snapshot_dir, "myset") == ["a", "b"]


def test_get_set_returns_none_for_missing(snapshot_dir):
    assert get_set(snapshot_dir, "ghost") is None


def test_get_set_returns_members(snapshot_dir):
    create_set(snapshot_dir, "myset", ["snap1", "snap2"])
    assert get_set(snapshot_dir, "myset") == ["snap1", "snap2"]


def test_delete_set_returns_true_when_found(snapshot_dir):
    create_set(snapshot_dir, "myset", ["snap1"])
    assert delete_set(snapshot_dir, "myset") is True


def test_delete_set_returns_false_when_missing(snapshot_dir):
    assert delete_set(snapshot_dir, "ghost") is False


def test_delete_set_removes_from_store(snapshot_dir):
    create_set(snapshot_dir, "myset", ["snap1"])
    delete_set(snapshot_dir, "myset")
    assert get_set(snapshot_dir, "myset") is None


def test_list_sets_returns_empty_dict_when_none(snapshot_dir):
    assert list_sets(snapshot_dir) == {}


def test_list_sets_returns_all_sets(snapshot_dir):
    create_set(snapshot_dir, "alpha", ["a"])
    create_set(snapshot_dir, "beta", ["b", "c"])
    result = list_sets(snapshot_dir)
    assert set(result.keys()) == {"alpha", "beta"}


def test_add_to_set_returns_true_when_new(snapshot_dir):
    create_set(snapshot_dir, "myset", ["snap1"])
    assert add_to_set(snapshot_dir, "myset", "snap2") is True


def test_add_to_set_returns_false_when_duplicate(snapshot_dir):
    create_set(snapshot_dir, "myset", ["snap1"])
    assert add_to_set(snapshot_dir, "myset", "snap1") is False


def test_add_to_set_raises_when_set_missing(snapshot_dir):
    with pytest.raises(SnapshotSetError):
        add_to_set(snapshot_dir, "ghost", "snap1")


def test_add_to_set_appends_member(snapshot_dir):
    create_set(snapshot_dir, "myset", ["snap1"])
    add_to_set(snapshot_dir, "myset", "snap2")
    assert get_set(snapshot_dir, "myset") == ["snap1", "snap2"]


def test_remove_from_set_returns_true_when_present(snapshot_dir):
    create_set(snapshot_dir, "myset", ["snap1", "snap2"])
    assert remove_from_set(snapshot_dir, "myset", "snap1") is True


def test_remove_from_set_returns_false_when_absent(snapshot_dir):
    create_set(snapshot_dir, "myset", ["snap1"])
    assert remove_from_set(snapshot_dir, "myset", "ghost") is False


def test_remove_from_set_updates_members(snapshot_dir):
    create_set(snapshot_dir, "myset", ["snap1", "snap2"])
    remove_from_set(snapshot_dir, "myset", "snap1")
    assert get_set(snapshot_dir, "myset") == ["snap2"]
