"""Tests for envforge.snapshot_reminder."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_reminder import (
    ReminderEntry,
    ReminderReport,
    add_reminder,
    get_reminders,
    remove_reminder,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_add_reminder_creates_reminders_file(snapshot_dir: Path) -> None:
    add_reminder(snapshot_dir, "snap1", "Review env", "2025-06-01")
    assert (snapshot_dir / "reminders.json").exists()


def test_add_reminder_returns_true_when_new(snapshot_dir: Path) -> None:
    result = add_reminder(snapshot_dir, "snap1", "Check vars", "2025-07-01")
    assert result is True


def test_add_reminder_returns_false_when_duplicate(snapshot_dir: Path) -> None:
    add_reminder(snapshot_dir, "snap1", "Check vars", "2025-07-01")
    result = add_reminder(snapshot_dir, "snap1", "Check vars", "2025-07-01")
    assert result is False


def test_add_reminder_stores_message(snapshot_dir: Path) -> None:
    add_reminder(snapshot_dir, "snap1", "Hello reminder", "2025-08-01")
    data = json.loads((snapshot_dir / "reminders.json").read_text())
    assert data["snap1"][0]["message"] == "Hello reminder"


def test_add_reminder_stores_recur(snapshot_dir: Path) -> None:
    add_reminder(snapshot_dir, "snap1", "Weekly check", "2025-09-01", recur="weekly")
    data = json.loads((snapshot_dir / "reminders.json").read_text())
    assert data["snap1"][0]["recur"] == "weekly"


def test_add_reminder_no_recur_defaults_none(snapshot_dir: Path) -> None:
    add_reminder(snapshot_dir, "snap1", "One-time", "2025-10-01")
    data = json.loads((snapshot_dir / "reminders.json").read_text())
    assert data["snap1"][0]["recur"] is None


def test_remove_reminder_returns_true_when_found(snapshot_dir: Path) -> None:
    add_reminder(snapshot_dir, "snap1", "msg", "2025-11-01")
    result = remove_reminder(snapshot_dir, "snap1", "2025-11-01")
    assert result is True


def test_remove_reminder_returns_false_when_missing(snapshot_dir: Path) -> None:
    result = remove_reminder(snapshot_dir, "snap1", "2025-11-01")
    assert result is False


def test_remove_reminder_deletes_entry(snapshot_dir: Path) -> None:
    add_reminder(snapshot_dir, "snap1", "msg", "2025-12-01")
    remove_reminder(snapshot_dir, "snap1", "2025-12-01")
    data = json.loads((snapshot_dir / "reminders.json").read_text())
    assert data["snap1"] == []


def test_get_reminders_returns_reminder_report(snapshot_dir: Path) -> None:
    report = get_reminders(snapshot_dir)
    assert isinstance(report, ReminderReport)


def test_get_reminders_is_empty_when_none(snapshot_dir: Path) -> None:
    report = get_reminders(snapshot_dir)
    assert report.is_empty()


def test_get_reminders_sorted_by_due(snapshot_dir: Path) -> None:
    add_reminder(snapshot_dir, "snap1", "later", "2026-01-01")
    add_reminder(snapshot_dir, "snap2", "earlier", "2025-01-01")
    report = get_reminders(snapshot_dir)
    assert report.entries[0].due == "2025-01-01"
    assert report.entries[1].due == "2026-01-01"


def test_for_snapshot_filters_correctly(snapshot_dir: Path) -> None:
    add_reminder(snapshot_dir, "snap1", "a", "2025-03-01")
    add_reminder(snapshot_dir, "snap2", "b", "2025-04-01")
    report = get_reminders(snapshot_dir)
    filtered = report.for_snapshot("snap1")
    assert all(e.snapshot == "snap1" for e in filtered)
    assert len(filtered) == 1


def test_due_before_filters_correctly(snapshot_dir: Path) -> None:
    add_reminder(snapshot_dir, "snap1", "early", "2025-01-15")
    add_reminder(snapshot_dir, "snap1", "late", "2026-06-01")
    report = get_reminders(snapshot_dir)
    due_entries = report.due_before("2025-12-31")
    assert len(due_entries) == 1
    assert due_entries[0].message == "early"
