"""Tests for envforge.history module."""

import json
import pytest
from pathlib import Path

from envforge.history import record_event, get_history, clear_history, HISTORY_FILE


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def test_record_event_creates_history_file(snapshot_dir):
    record_event(snapshot_dir, "mysnap", "save")
    assert (snapshot_dir / HISTORY_FILE).exists()


def test_record_event_returns_entry(snapshot_dir):
    entry = record_event(snapshot_dir, "mysnap", "save")
    assert entry["snapshot"] == "mysnap"
    assert entry["action"] == "save"
    assert "timestamp" in entry


def test_record_event_appends_multiple(snapshot_dir):
    record_event(snapshot_dir, "snap1", "save")
    record_event(snapshot_dir, "snap2", "restore")
    entries = get_history(snapshot_dir)
    assert len(entries) == 2


def test_record_event_stores_optional_note(snapshot_dir):
    record_event(snapshot_dir, "snap1", "save", note="initial capture")
    entries = get_history(snapshot_dir)
    assert entries[0]["note"] == "initial capture"


def test_record_event_no_note_key_when_absent(snapshot_dir):
    record_event(snapshot_dir, "snap1", "save")
    entries = get_history(snapshot_dir)
    assert "note" not in entries[0]


def test_get_history_filter_by_snapshot(snapshot_dir):
    record_event(snapshot_dir, "snap1", "save")
    record_event(snapshot_dir, "snap2", "save")
    record_event(snapshot_dir, "snap1", "restore")
    result = get_history(snapshot_dir, snapshot_name="snap1")
    assert len(result) == 2
    assert all(e["snapshot"] == "snap1" for e in result)


def test_get_history_filter_by_action(snapshot_dir):
    record_event(snapshot_dir, "snap1", "save")
    record_event(snapshot_dir, "snap2", "restore")
    record_event(snapshot_dir, "snap3", "save")
    result = get_history(snapshot_dir, action="save")
    assert len(result) == 2
    assert all(e["action"] == "save" for e in result)


def test_get_history_limit(snapshot_dir):
    for i in range(5):
        record_event(snapshot_dir, f"snap{i}", "save")
    result = get_history(snapshot_dir, limit=3)
    assert len(result) == 3
    assert result[-1]["snapshot"] == "snap4"


def test_get_history_empty_when_no_file(snapshot_dir):
    result = get_history(snapshot_dir)
    assert result == []


def test_clear_history_all(snapshot_dir):
    record_event(snapshot_dir, "snap1", "save")
    record_event(snapshot_dir, "snap2", "save")
    removed = clear_history(snapshot_dir)
    assert removed == 2
    assert get_history(snapshot_dir) == []


def test_clear_history_by_snapshot(snapshot_dir):
    record_event(snapshot_dir, "snap1", "save")
    record_event(snapshot_dir, "snap2", "save")
    record_event(snapshot_dir, "snap1", "restore")
    removed = clear_history(snapshot_dir, snapshot_name="snap1")
    assert removed == 2
    remaining = get_history(snapshot_dir)
    assert len(remaining) == 1
    assert remaining[0]["snapshot"] == "snap2"


def test_clear_history_returns_zero_when_nothing_matches(snapshot_dir):
    record_event(snapshot_dir, "snap1", "save")
    removed = clear_history(snapshot_dir, snapshot_name="nonexistent")
    assert removed == 0
