"""Tests for envforge.snapshot_revert."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_revert import (
    RevertError,
    RevertResult,
    list_revert_points,
    revert_snapshot,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


def _write_history(snapshot_dir: Path, entries: list[dict]) -> None:
    (snapshot_dir / "history.json").write_text(json.dumps(entries))


# ---------------------------------------------------------------------------
# list_revert_points
# ---------------------------------------------------------------------------

def test_list_revert_points_empty_when_no_history(snapshot_dir):
    points = list_revert_points("mysnap", snapshot_dir)
    assert points == []


def test_list_revert_points_returns_matching_entries(snapshot_dir):
    _write_history(snapshot_dir, [
        {"snapshot": "mysnap", "timestamp": "2024-01-01T00:00:00", "vars": {"A": "1"}},
        {"snapshot": "other", "timestamp": "2024-01-02T00:00:00", "vars": {"B": "2"}},
    ])
    points = list_revert_points("mysnap", snapshot_dir)
    assert len(points) == 1
    assert points[0]["snapshot"] == "mysnap"


def test_list_revert_points_excludes_entries_without_vars(snapshot_dir):
    _write_history(snapshot_dir, [
        {"snapshot": "mysnap", "timestamp": "2024-01-01T00:00:00"},
        {"snapshot": "mysnap", "timestamp": "2024-01-02T00:00:00", "vars": {"A": "1"}},
    ])
    points = list_revert_points("mysnap", snapshot_dir)
    assert len(points) == 1


# ---------------------------------------------------------------------------
# revert_snapshot
# ---------------------------------------------------------------------------

def test_revert_raises_when_no_revert_points(snapshot_dir):
    _write(snapshot_dir, "mysnap", {"A": "1"})
    with pytest.raises(RevertError, match="No revert points"):
        revert_snapshot("mysnap", snapshot_dir)


def test_revert_raises_for_out_of_range_index(snapshot_dir):
    _write(snapshot_dir, "mysnap", {"A": "1"})
    _write_history(snapshot_dir, [
        {"snapshot": "mysnap", "timestamp": "T1", "vars": {"A": "old"}},
    ])
    with pytest.raises(RevertError, match="out of range"):
        revert_snapshot("mysnap", snapshot_dir, index=5)


def test_revert_raises_for_unknown_timestamp(snapshot_dir):
    _write(snapshot_dir, "mysnap", {"A": "1"})
    _write_history(snapshot_dir, [
        {"snapshot": "mysnap", "timestamp": "T1", "vars": {"A": "old"}},
    ])
    with pytest.raises(RevertError, match="timestamp"):
        revert_snapshot("mysnap", snapshot_dir, timestamp="NOPE")


def test_revert_returns_revert_result(snapshot_dir):
    _write(snapshot_dir, "mysnap", {"A": "new"})
    _write_history(snapshot_dir, [
        {"snapshot": "mysnap", "timestamp": "T1", "vars": {"A": "old"}},
    ])
    result = revert_snapshot("mysnap", snapshot_dir)
    assert isinstance(result, RevertResult)


def test_revert_restores_previous_vars(snapshot_dir):
    _write(snapshot_dir, "mysnap", {"A": "new"})
    _write_history(snapshot_dir, [
        {"snapshot": "mysnap", "timestamp": "T1", "vars": {"A": "old"}},
    ])
    revert_snapshot("mysnap", snapshot_dir)
    data = json.loads((snapshot_dir / "mysnap.json").read_text())
    assert data["A"] == "old"


def test_revert_records_changed_keys(snapshot_dir):
    _write(snapshot_dir, "mysnap", {"A": "1", "B": "2"})
    _write_history(snapshot_dir, [
        {"snapshot": "mysnap", "timestamp": "T1", "vars": {"A": "old", "C": "3"}},
    ])
    result = revert_snapshot("mysnap", snapshot_dir)
    assert set(result.keys_changed) == {"A", "B", "C"}


def test_revert_by_timestamp(snapshot_dir):
    _write(snapshot_dir, "mysnap", {"A": "current"})
    _write_history(snapshot_dir, [
        {"snapshot": "mysnap", "timestamp": "T1", "vars": {"A": "v1"}},
        {"snapshot": "mysnap", "timestamp": "T2", "vars": {"A": "v2"}},
    ])
    result = revert_snapshot("mysnap", snapshot_dir, timestamp="T2")
    assert result.restored_vars["A"] == "v2"


def test_revert_total_changed_property(snapshot_dir):
    _write(snapshot_dir, "mysnap", {"A": "1"})
    _write_history(snapshot_dir, [
        {"snapshot": "mysnap", "timestamp": "T1", "vars": {"A": "old", "B": "2"}},
    ])
    result = revert_snapshot("mysnap", snapshot_dir)
    assert result.total_changed == len(result.keys_changed)
