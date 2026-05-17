"""Tests for envforge.snapshot_event."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_event import (
    EventEntry,
    EventLog,
    clear_events,
    get_event_log,
    record_event,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_record_event_creates_events_file(snapshot_dir: Path) -> None:
    record_event(snapshot_dir, "snap1", "created")
    assert (snapshot_dir / "_events.json").exists()


def test_record_event_returns_entry(snapshot_dir: Path) -> None:
    entry = record_event(snapshot_dir, "snap1", "updated")
    assert isinstance(entry, EventEntry)
    assert entry.snapshot == "snap1"
    assert entry.event == "updated"


def test_record_event_stores_user(snapshot_dir: Path) -> None:
    entry = record_event(snapshot_dir, "snap1", "deleted", user="alice")
    assert entry.user == "alice"


def test_record_event_stores_note(snapshot_dir: Path) -> None:
    entry = record_event(snapshot_dir, "snap1", "restored", note="hotfix")
    assert entry.note == "hotfix"


def test_record_event_appends_multiple(snapshot_dir: Path) -> None:
    record_event(snapshot_dir, "snap1", "created")
    record_event(snapshot_dir, "snap1", "updated")
    log = get_event_log(snapshot_dir)
    assert len(log) == 2


def test_get_event_log_returns_event_log(snapshot_dir: Path) -> None:
    log = get_event_log(snapshot_dir)
    assert isinstance(log, EventLog)


def test_event_log_is_empty_when_no_events(snapshot_dir: Path) -> None:
    log = get_event_log(snapshot_dir)
    assert log.is_empty()


def test_event_log_for_snapshot_filters_correctly(snapshot_dir: Path) -> None:
    record_event(snapshot_dir, "snap1", "created")
    record_event(snapshot_dir, "snap2", "created")
    log = get_event_log(snapshot_dir)
    assert len(log.for_snapshot("snap1")) == 1


def test_event_log_by_event_filters_correctly(snapshot_dir: Path) -> None:
    record_event(snapshot_dir, "snap1", "created")
    record_event(snapshot_dir, "snap1", "updated")
    log = get_event_log(snapshot_dir)
    assert len(log.by_event("created")) == 1


def test_clear_events_removes_for_snapshot(snapshot_dir: Path) -> None:
    record_event(snapshot_dir, "snap1", "created")
    record_event(snapshot_dir, "snap2", "created")
    removed = clear_events(snapshot_dir, snapshot="snap1")
    assert removed == 1
    log = get_event_log(snapshot_dir)
    assert len(log.for_snapshot("snap1")) == 0
    assert len(log.for_snapshot("snap2")) == 1


def test_clear_events_all_when_no_snapshot_given(snapshot_dir: Path) -> None:
    record_event(snapshot_dir, "snap1", "created")
    record_event(snapshot_dir, "snap2", "created")
    removed = clear_events(snapshot_dir)
    assert removed == 2
    assert get_event_log(snapshot_dir).is_empty()


def test_record_event_timestamp_is_stored(snapshot_dir: Path) -> None:
    record_event(snapshot_dir, "snap1", "created")
    data = json.loads((snapshot_dir / "_events.json").read_text())
    assert "timestamp" in data[0]
