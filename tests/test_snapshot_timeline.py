"""Tests for envforge.snapshot_timeline."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from envforge.snapshot_timeline import (
    SnapshotTimeline,
    TimelineEvent,
    build_timeline,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _fake_history(entries):
    return patch("envforge.snapshot_timeline.get_history", return_value=entries)


def _entry(snapshot, action, timestamp, note=None):
    e = {"snapshot": snapshot, "action": action, "timestamp": timestamp}
    if note:
        e["note"] = note
    return e


def test_build_timeline_returns_snapshot_timeline(snapshot_dir):
    with _fake_history([]):
        result = build_timeline(snapshot_dir)
    assert isinstance(result, SnapshotTimeline)


def test_build_timeline_is_empty_when_no_history(snapshot_dir):
    with _fake_history([]):
        result = build_timeline(snapshot_dir)
    assert result.is_empty()


def test_build_timeline_creates_event_per_entry(snapshot_dir):
    entries = [
        _entry("snap_a", "save", "2024-01-01T10:00:00"),
        _entry("snap_b", "delete", "2024-01-02T11:00:00"),
    ]
    with _fake_history(entries):
        result = build_timeline(snapshot_dir)
    assert len(result.events) == 2


def test_build_timeline_event_fields(snapshot_dir):
    entries = [_entry("mysnap", "save", "2024-03-01T09:00:00", note="initial")]
    with _fake_history(entries):
        result = build_timeline(snapshot_dir)
    ev = result.events[0]
    assert ev.snapshot == "mysnap"
    assert ev.action == "save"
    assert ev.timestamp == "2024-03-01T09:00:00"
    assert ev.note == "initial"


def test_build_timeline_filters_by_name(snapshot_dir):
    entries = [
        _entry("snap_a", "save", "2024-01-01T10:00:00"),
        _entry("snap_b", "delete", "2024-01-02T11:00:00"),
    ]
    with _fake_history(entries):
        result = build_timeline(snapshot_dir, name="snap_a")
    assert len(result.events) == 1
    assert result.events[0].snapshot == "snap_a"


def test_for_snapshot_filters_events(snapshot_dir):
    entries = [
        _entry("snap_a", "save", "2024-01-01T10:00:00"),
        _entry("snap_a", "restore", "2024-01-03T12:00:00"),
        _entry("snap_b", "save", "2024-01-02T11:00:00"),
    ]
    with _fake_history(entries):
        result = build_timeline(snapshot_dir)
    filtered = result.for_snapshot("snap_a")
    assert len(filtered.events) == 2
    assert all(e.snapshot == "snap_a" for e in filtered.events)


def test_sorted_events_ascending(snapshot_dir):
    entries = [
        _entry("snap_a", "restore", "2024-01-03T00:00:00"),
        _entry("snap_a", "save", "2024-01-01T00:00:00"),
    ]
    with _fake_history(entries):
        result = build_timeline(snapshot_dir)
    sorted_ev = result.sorted_events(descending=False)
    assert sorted_ev[0].timestamp < sorted_ev[1].timestamp


def test_sorted_events_descending(snapshot_dir):
    entries = [
        _entry("snap_a", "save", "2024-01-01T00:00:00"),
        _entry("snap_a", "restore", "2024-01-03T00:00:00"),
    ]
    with _fake_history(entries):
        result = build_timeline(snapshot_dir)
    sorted_ev = result.sorted_events(descending=True)
    assert sorted_ev[0].timestamp > sorted_ev[1].timestamp


def test_actions_returns_unique_actions(snapshot_dir):
    entries = [
        _entry("snap_a", "save", "2024-01-01T00:00:00"),
        _entry("snap_a", "save", "2024-01-02T00:00:00"),
        _entry("snap_b", "delete", "2024-01-03T00:00:00"),
    ]
    with _fake_history(entries):
        result = build_timeline(snapshot_dir)
    assert set(result.actions()) == {"save", "delete"}
