"""Tests for envforge.group."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envforge.group import (
    add_to_group,
    remove_from_group,
    list_groups,
    get_group,
    delete_group,
    _groups_path,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_add_to_group_creates_groups_file(snapshot_dir):
    add_to_group(snapshot_dir, "prod", "snap1")
    assert _groups_path(snapshot_dir).exists()


def test_add_to_group_stores_snapshot(snapshot_dir):
    add_to_group(snapshot_dir, "prod", "snap1")
    data = json.loads(_groups_path(snapshot_dir).read_text())
    assert "snap1" in data["prod"]


def test_add_to_group_returns_true_when_new(snapshot_dir):
    result = add_to_group(snapshot_dir, "prod", "snap1")
    assert result is True


def test_add_to_group_returns_false_when_duplicate(snapshot_dir):
    add_to_group(snapshot_dir, "prod", "snap1")
    result = add_to_group(snapshot_dir, "prod", "snap1")
    assert result is False


def test_add_to_group_allows_multiple_snapshots(snapshot_dir):
    add_to_group(snapshot_dir, "prod", "snap1")
    add_to_group(snapshot_dir, "prod", "snap2")
    members = get_group(snapshot_dir, "prod")
    assert "snap1" in members
    assert "snap2" in members


def test_remove_from_group_returns_true_when_found(snapshot_dir):
    add_to_group(snapshot_dir, "prod", "snap1")
    result = remove_from_group(snapshot_dir, "prod", "snap1")
    assert result is True


def test_remove_from_group_returns_false_when_missing(snapshot_dir):
    result = remove_from_group(snapshot_dir, "prod", "nonexistent")
    assert result is False


def test_remove_from_group_deletes_empty_group(snapshot_dir):
    add_to_group(snapshot_dir, "prod", "snap1")
    remove_from_group(snapshot_dir, "prod", "snap1")
    assert get_group(snapshot_dir, "prod") is None


def test_list_groups_returns_empty_dict_when_no_file(snapshot_dir):
    assert list_groups(snapshot_dir) == {}


def test_list_groups_returns_all_groups(snapshot_dir):
    add_to_group(snapshot_dir, "prod", "snap1")
    add_to_group(snapshot_dir, "dev", "snap2")
    groups = list_groups(snapshot_dir)
    assert "prod" in groups
    assert "dev" in groups


def test_get_group_returns_none_for_missing(snapshot_dir):
    assert get_group(snapshot_dir, "ghost") is None


def test_delete_group_returns_true_when_found(snapshot_dir):
    add_to_group(snapshot_dir, "prod", "snap1")
    result = delete_group(snapshot_dir, "prod")
    assert result is True


def test_delete_group_returns_false_when_missing(snapshot_dir):
    result = delete_group(snapshot_dir, "ghost")
    assert result is False


def test_delete_group_removes_group(snapshot_dir):
    add_to_group(snapshot_dir, "prod", "snap1")
    delete_group(snapshot_dir, "prod")
    assert get_group(snapshot_dir, "prod") is None
