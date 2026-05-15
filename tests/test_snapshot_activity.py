"""Tests for envforge.snapshot_activity."""
from __future__ import annotations

from pathlib import Path

import pytest

from envforge.snapshot_activity import (
    ActivityEntry,
    ActivityReport,
    clear_activity,
    get_activity,
    record_activity,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envforge"
    d.mkdir()
    return d


def test_record_activity_creates_activity_file(snapshot_dir: Path) -> None:
    record_activity(snapshot_dir, "prod", "write")
    assert (snapshot_dir / "activity.json").exists()


def test_record_activity_returns_entry(snapshot_dir: Path) -> None:
    entry = record_activity(snapshot_dir, "prod", "read")
    assert isinstance(entry, ActivityEntry)
    assert entry.snapshot == "prod"
    assert entry.action == "read"


def test_record_activity_stores_user(snapshot_dir: Path) -> None:
    entry = record_activity(snapshot_dir, "dev", "write", user="alice")
    assert entry.user == "alice"


def test_record_activity_appends_multiple(snapshot_dir: Path) -> None:
    record_activity(snapshot_dir, "prod", "write")
    record_activity(snapshot_dir, "prod", "read")
    report = get_activity(snapshot_dir)
    assert len(report.entries) == 2


def test_get_activity_returns_activity_report(snapshot_dir: Path) -> None:
    record_activity(snapshot_dir, "prod", "delete")
    report = get_activity(snapshot_dir)
    assert isinstance(report, ActivityReport)


def test_get_activity_is_empty_when_no_events(snapshot_dir: Path) -> None:
    report = get_activity(snapshot_dir)
    assert report.is_empty()


def test_get_activity_filters_by_snapshot(snapshot_dir: Path) -> None:
    record_activity(snapshot_dir, "prod", "read")
    record_activity(snapshot_dir, "dev", "write")
    report = get_activity(snapshot_dir, snapshot="prod")
    assert len(report.entries) == 1
    assert report.entries[0].snapshot == "prod"


def test_activity_report_by_action(snapshot_dir: Path) -> None:
    record_activity(snapshot_dir, "prod", "read")
    record_activity(snapshot_dir, "prod", "write")
    report = get_activity(snapshot_dir).by_action("read")
    assert all(e.action == "read" for e in report.entries)


def test_activity_report_most_recent_returns_last(snapshot_dir: Path) -> None:
    record_activity(snapshot_dir, "prod", "read")
    record_activity(snapshot_dir, "prod", "write")
    latest = get_activity(snapshot_dir).most_recent()
    assert latest is not None
    assert latest.action == "write"


def test_activity_report_most_recent_none_when_empty(snapshot_dir: Path) -> None:
    report = ActivityReport()
    assert report.most_recent() is None


def test_clear_activity_removes_all(snapshot_dir: Path) -> None:
    record_activity(snapshot_dir, "prod", "read")
    record_activity(snapshot_dir, "dev", "write")
    removed = clear_activity(snapshot_dir)
    assert removed == 2
    assert get_activity(snapshot_dir).is_empty()


def test_clear_activity_removes_specific_snapshot(snapshot_dir: Path) -> None:
    record_activity(snapshot_dir, "prod", "read")
    record_activity(snapshot_dir, "dev", "write")
    removed = clear_activity(snapshot_dir, snapshot="prod")
    assert removed == 1
    report = get_activity(snapshot_dir)
    assert len(report.entries) == 1
    assert report.entries[0].snapshot == "dev"
