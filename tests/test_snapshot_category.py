"""Tests for envforge.snapshot_category."""
import json
import pytest
from pathlib import Path

from envforge.snapshot_category import (
    add_to_category,
    remove_from_category,
    list_categories,
    get_category_members,
    find_categories_for,
    delete_category,
    _categories_path,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_add_creates_categories_file(snapshot_dir):
    add_to_category(snapshot_dir, "prod", "snap1")
    assert _categories_path(snapshot_dir).exists()


def test_add_stores_snapshot_in_category(snapshot_dir):
    add_to_category(snapshot_dir, "prod", "snap1")
    data = json.loads(_categories_path(snapshot_dir).read_text())
    assert "snap1" in data["prod"]


def test_add_returns_true_when_new(snapshot_dir):
    result = add_to_category(snapshot_dir, "prod", "snap1")
    assert result is True


def test_add_returns_false_when_duplicate(snapshot_dir):
    add_to_category(snapshot_dir, "prod", "snap1")
    result = add_to_category(snapshot_dir, "prod", "snap1")
    assert result is False


def test_add_multiple_snapshots_to_same_category(snapshot_dir):
    add_to_category(snapshot_dir, "prod", "snap1")
    add_to_category(snapshot_dir, "prod", "snap2")
    members = get_category_members(snapshot_dir, "prod")
    assert "snap1" in members
    assert "snap2" in members


def test_remove_returns_true_when_found(snapshot_dir):
    add_to_category(snapshot_dir, "prod", "snap1")
    result = remove_from_category(snapshot_dir, "prod", "snap1")
    assert result is True


def test_remove_returns_false_when_not_found(snapshot_dir):
    result = remove_from_category(snapshot_dir, "prod", "snap1")
    assert result is False


def test_remove_deletes_empty_category(snapshot_dir):
    add_to_category(snapshot_dir, "prod", "snap1")
    remove_from_category(snapshot_dir, "prod", "snap1")
    assert "prod" not in json.loads(_categories_path(snapshot_dir).read_text())


def test_list_categories_returns_sorted(snapshot_dir):
    add_to_category(snapshot_dir, "zebra", "s1")
    add_to_category(snapshot_dir, "alpha", "s2")
    cats = list_categories(snapshot_dir)
    assert cats == ["alpha", "zebra"]


def test_list_categories_empty_when_none(snapshot_dir):
    assert list_categories(snapshot_dir) == []


def test_get_category_members_returns_members(snapshot_dir):
    add_to_category(snapshot_dir, "dev", "snap-a")
    add_to_category(snapshot_dir, "dev", "snap-b")
    members = get_category_members(snapshot_dir, "dev")
    assert set(members) == {"snap-a", "snap-b"}


def test_get_category_members_empty_for_unknown(snapshot_dir):
    assert get_category_members(snapshot_dir, "nonexistent") == []


def test_find_categories_for_snapshot(snapshot_dir):
    add_to_category(snapshot_dir, "prod", "snap1")
    add_to_category(snapshot_dir, "stable", "snap1")
    cats = find_categories_for(snapshot_dir, "snap1")
    assert set(cats) == {"prod", "stable"}


def test_find_categories_for_returns_empty_when_not_categorized(snapshot_dir):
    assert find_categories_for(snapshot_dir, "snap1") == []


def test_delete_category_returns_true_when_exists(snapshot_dir):
    add_to_category(snapshot_dir, "old", "snap1")
    assert delete_category(snapshot_dir, "old") is True


def test_delete_category_returns_false_when_missing(snapshot_dir):
    assert delete_category(snapshot_dir, "ghost") is False


def test_delete_category_removes_all_members(snapshot_dir):
    add_to_category(snapshot_dir, "temp", "snap1")
    add_to_category(snapshot_dir, "temp", "snap2")
    delete_category(snapshot_dir, "temp")
    assert get_category_members(snapshot_dir, "temp") == []
