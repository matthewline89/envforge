"""Tests for envforge.merge module."""

from __future__ import annotations

import json
import os
import pytest

from envforge.merge import merge_dicts, merge_snapshots, save_merge, MergeResult
from envforge.snapshot import save


@pytest.fixture()
def snapshot_dir(tmp_path):
    return str(tmp_path)


# --- merge_dicts ---

def test_merge_dicts_combines_keys():
    result = merge_dicts({"A": "1"}, {"B": "2"})
    assert result == {"A": "1", "B": "2"}


def test_merge_dicts_override_wins_by_default():
    result = merge_dicts({"A": "1"}, {"A": "99"})
    assert result["A"] == "99"


def test_merge_dicts_records_conflict():
    conflicts: dict = {}
    merge_dicts({"A": "1"}, {"A": "2"}, conflicts=conflicts)
    assert "A" in conflicts
    assert conflicts["A"] == ["1", "2"]


def test_merge_dicts_no_conflict_when_values_equal():
    conflicts: dict = {}
    merge_dicts({"A": "1"}, {"A": "1"}, conflicts=conflicts)
    assert "A" not in conflicts


# --- merge_snapshots ---

def test_merge_snapshots_requires_two_or_more(snapshot_dir):
    save({"X": "1"}, "only", snapshot_dir)
    with pytest.raises(ValueError, match="At least two"):
        merge_snapshots(["only"], snapshot_dir)


def test_merge_snapshots_last_wins(snapshot_dir):
    save({"A": "first", "B": "shared"}, "snap1", snapshot_dir)
    save({"B": "override", "C": "new"}, "snap2", snapshot_dir)
    result = merge_snapshots(["snap1", "snap2"], snapshot_dir, strategy="last-wins")
    assert result.merged["A"] == "first"
    assert result.merged["B"] == "override"
    assert result.merged["C"] == "new"


def test_merge_snapshots_first_wins(snapshot_dir):
    save({"A": "keep", "B": "shared"}, "snap1", snapshot_dir)
    save({"B": "ignore", "C": "new"}, "snap2", snapshot_dir)
    result = merge_snapshots(["snap1", "snap2"], snapshot_dir, strategy="first-wins")
    assert result.merged["B"] == "keep"


def test_merge_snapshots_records_sources(snapshot_dir):
    save({"A": "1"}, "s1", snapshot_dir)
    save({"B": "2"}, "s2", snapshot_dir)
    result = merge_snapshots(["s1", "s2"], snapshot_dir)
    assert result.sources == ["s1", "s2"]


def test_merge_snapshots_raises_on_missing_file(snapshot_dir):
    save({"A": "1"}, "exists", snapshot_dir)
    with pytest.raises(FileNotFoundError):
        merge_snapshots(["exists", "ghost"], snapshot_dir)


# --- save_merge ---

def test_save_merge_creates_file(snapshot_dir):
    save({"A": "1"}, "a", snapshot_dir)
    save({"B": "2"}, "b", snapshot_dir)
    result = merge_snapshots(["a", "b"], snapshot_dir)
    path = save_merge(result, "combined", snapshot_dir)
    assert os.path.isfile(path)


def test_save_merge_file_contains_merged_data(snapshot_dir):
    save({"A": "1"}, "a", snapshot_dir)
    save({"B": "2"}, "b", snapshot_dir)
    result = merge_snapshots(["a", "b"], snapshot_dir)
    path = save_merge(result, "combined", snapshot_dir)
    with open(path) as fh:
        data = json.load(fh)
    assert data["A"] == "1"
    assert data["B"] == "2"
