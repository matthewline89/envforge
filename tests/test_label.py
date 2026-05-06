"""Tests for envforge.label."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.label import (
    add_label,
    clear_labels,
    find_by_label,
    get_labels,
    list_labels,
    remove_label,
    _labels_path,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_add_label_creates_labels_file(snapshot_dir):
    add_label(snapshot_dir, "snap1", "production")
    assert _labels_path(snapshot_dir).exists()


def test_add_label_stores_mapping(snapshot_dir):
    add_label(snapshot_dir, "snap1", "production")
    data = json.loads(_labels_path(snapshot_dir).read_text())
    assert "production" in data["snap1"]


def test_add_label_returns_true_when_new(snapshot_dir):
    assert add_label(snapshot_dir, "snap1", "ci") is True


def test_add_label_returns_false_when_duplicate(snapshot_dir):
    add_label(snapshot_dir, "snap1", "ci")
    assert add_label(snapshot_dir, "snap1", "ci") is False


def test_add_multiple_labels_to_same_snapshot(snapshot_dir):
    add_label(snapshot_dir, "snap1", "production")
    add_label(snapshot_dir, "snap1", "stable")
    labels = get_labels(snapshot_dir, "snap1")
    assert "production" in labels
    assert "stable" in labels


def test_remove_label_returns_true_when_found(snapshot_dir):
    add_label(snapshot_dir, "snap1", "old")
    assert remove_label(snapshot_dir, "snap1", "old") is True


def test_remove_label_returns_false_when_missing(snapshot_dir):
    assert remove_label(snapshot_dir, "snap1", "ghost") is False


def test_remove_label_no_longer_in_list(snapshot_dir):
    add_label(snapshot_dir, "snap1", "temp")
    remove_label(snapshot_dir, "snap1", "temp")
    assert "temp" not in get_labels(snapshot_dir, "snap1")


def test_get_labels_returns_empty_for_unknown(snapshot_dir):
    assert get_labels(snapshot_dir, "nonexistent") == []


def test_find_by_label_returns_matching_snapshots(snapshot_dir):
    add_label(snapshot_dir, "snap1", "deploy")
    add_label(snapshot_dir, "snap2", "deploy")
    add_label(snapshot_dir, "snap3", "test")
    result = find_by_label(snapshot_dir, "deploy")
    assert "snap1" in result
    assert "snap2" in result
    assert "snap3" not in result


def test_find_by_label_returns_empty_when_none_match(snapshot_dir):
    assert find_by_label(snapshot_dir, "nonexistent") == []


def test_list_labels_returns_full_mapping(snapshot_dir):
    add_label(snapshot_dir, "snap1", "a")
    add_label(snapshot_dir, "snap2", "b")
    data = list_labels(snapshot_dir)
    assert "snap1" in data
    assert "snap2" in data


def test_clear_labels_removes_all(snapshot_dir):
    add_label(snapshot_dir, "snap1", "x")
    add_label(snapshot_dir, "snap1", "y")
    removed = clear_labels(snapshot_dir, "snap1")
    assert removed == 2
    assert get_labels(snapshot_dir, "snap1") == []


def test_clear_labels_returns_zero_for_unknown(snapshot_dir):
    assert clear_labels(snapshot_dir, "ghost") == 0
