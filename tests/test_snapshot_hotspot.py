"""Tests for envforge.snapshot_hotspot."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_hotspot import HotspotEntry, HotspotReport, compute_hotspots


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


def _write_history(snapshot_dir: Path, events: list) -> None:
    history_file = snapshot_dir / "history.json"
    history_file.write_text(json.dumps(events))


def test_compute_hotspots_returns_hotspot_report(snapshot_dir):
    _write(snapshot_dir, "snap1", {"KEY": "val"})
    _write_history(snapshot_dir, [{"snapshot": "snap1", "action": "save"}])
    result = compute_hotspots(snapshot_dir)
    assert isinstance(result, HotspotReport)


def test_compute_hotspots_empty_when_no_history(snapshot_dir):
    _write(snapshot_dir, "snap1", {"KEY": "val"})
    result = compute_hotspots(snapshot_dir)
    assert result.is_empty()


def test_compute_hotspots_counts_key(snapshot_dir):
    _write(snapshot_dir, "snap1", {"FOO": "bar"})
    _write_history(snapshot_dir, [{"snapshot": "snap1", "action": "save"}])
    result = compute_hotspots(snapshot_dir)
    keys = [e.key for e in result.entries]
    assert "FOO" in keys


def test_compute_hotspots_change_count_increments_across_snapshots(snapshot_dir):
    _write(snapshot_dir, "snap1", {"SHARED": "a"})
    _write(snapshot_dir, "snap2", {"SHARED": "b"})
    _write_history(
        snapshot_dir,
        [
            {"snapshot": "snap1", "action": "save"},
            {"snapshot": "snap2", "action": "save"},
        ],
    )
    result = compute_hotspots(snapshot_dir)
    entry = next(e for e in result.entries if e.key == "SHARED")
    assert entry.change_count == 2


def test_compute_hotspots_no_duplicate_count_for_same_snapshot(snapshot_dir):
    _write(snapshot_dir, "snap1", {"FOO": "x"})
    _write_history(
        snapshot_dir,
        [
            {"snapshot": "snap1", "action": "save"},
            {"snapshot": "snap1", "action": "save"},
        ],
    )
    result = compute_hotspots(snapshot_dir)
    entry = next(e for e in result.entries if e.key == "FOO")
    assert entry.change_count == 1


def test_hotspot_entry_stores_snapshot_names(snapshot_dir):
    _write(snapshot_dir, "snap1", {"KEY": "v"})
    _write_history(snapshot_dir, [{"snapshot": "snap1", "action": "save"}])
    result = compute_hotspots(snapshot_dir)
    entry = next(e for e in result.entries if e.key == "KEY")
    assert "snap1" in entry.snapshots


def test_top_returns_limited_entries(snapshot_dir):
    for i in range(8):
        _write(snapshot_dir, f"snap{i}", {f"KEY{i}": "val"})
    events = [{"snapshot": f"snap{i}", "action": "save"} for i in range(8)]
    _write_history(snapshot_dir, events)
    result = compute_hotspots(snapshot_dir, top_n=8)
    assert len(result.top(3)) == 3


def test_hotspot_report_is_empty_false_with_entries(snapshot_dir):
    _write(snapshot_dir, "snap1", {"A": "1"})
    _write_history(snapshot_dir, [{"snapshot": "snap1", "action": "save"}])
    result = compute_hotspots(snapshot_dir)
    assert not result.is_empty()


def test_compute_hotspots_skips_missing_snapshot(snapshot_dir):
    _write_history(snapshot_dir, [{"snapshot": "ghost", "action": "save"}])
    result = compute_hotspots(snapshot_dir)
    assert result.is_empty()


def test_hotspot_entry_dataclass_fields():
    entry = HotspotEntry(key="X", change_count=3, snapshots=["a", "b"])
    assert entry.key == "X"
    assert entry.change_count == 3
    assert entry.snapshots == ["a", "b"]
