"""Tests for envforge.snapshot_streak."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from envforge.snapshot_streak import (
    StreakEntry,
    StreakReport,
    compute_streak,
    record_activity,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _iso(delta: int = 0) -> str:
    return (date.today() + timedelta(days=delta)).isoformat()


def test_record_activity_creates_streaks_file(snapshot_dir):
    record_activity(snapshot_dir, "env1")
    assert (snapshot_dir / "streaks.json").exists()


def test_record_activity_returns_entry(snapshot_dir):
    entry = record_activity(snapshot_dir, "env1")
    assert isinstance(entry, StreakEntry)
    assert entry.snapshot == "env1"


def test_record_activity_stores_date(snapshot_dir):
    entry = record_activity(snapshot_dir, "env1", on_date="2024-06-01")
    assert entry.date == "2024-06-01"


def test_record_activity_deduplicates_same_date(snapshot_dir):
    record_activity(snapshot_dir, "env1", on_date="2024-06-01")
    record_activity(snapshot_dir, "env1", on_date="2024-06-01")
    report = compute_streak(snapshot_dir, "env1")
    assert report.dates.count("2024-06-01") == 1


def test_compute_streak_empty_for_unknown_snapshot(snapshot_dir):
    report = compute_streak(snapshot_dir, "missing")
    assert report.is_empty()
    assert report.current_streak == 0
    assert report.longest_streak == 0


def test_compute_streak_returns_streak_report(snapshot_dir):
    record_activity(snapshot_dir, "env1", on_date="2024-01-01")
    report = compute_streak(snapshot_dir, "env1")
    assert isinstance(report, StreakReport)


def test_compute_streak_single_day_longest_is_one(snapshot_dir):
    record_activity(snapshot_dir, "env1", on_date="2024-01-01")
    report = compute_streak(snapshot_dir, "env1")
    assert report.longest_streak == 1


def test_compute_streak_consecutive_days_increases_longest(snapshot_dir):
    for d in ["2024-01-01", "2024-01-02", "2024-01-03"]:
        record_activity(snapshot_dir, "env1", on_date=d)
    report = compute_streak(snapshot_dir, "env1")
    assert report.longest_streak == 3


def test_compute_streak_gap_resets_current(snapshot_dir):
    for d in ["2024-01-01", "2024-01-03"]:
        record_activity(snapshot_dir, "env1", on_date=d)
    report = compute_streak(snapshot_dir, "env1")
    assert report.longest_streak == 1


def test_compute_streak_current_streak_active_today(snapshot_dir):
    today = _iso(0)
    yesterday = _iso(-1)
    record_activity(snapshot_dir, "env1", on_date=yesterday)
    record_activity(snapshot_dir, "env1", on_date=today)
    report = compute_streak(snapshot_dir, "env1")
    assert report.current_streak == 2


def test_compute_streak_current_streak_zero_after_gap(snapshot_dir):
    record_activity(snapshot_dir, "env1", on_date="2020-01-01")
    report = compute_streak(snapshot_dir, "env1")
    assert report.current_streak == 0


def test_multiple_snapshots_tracked_independently(snapshot_dir):
    record_activity(snapshot_dir, "a", on_date="2024-03-01")
    record_activity(snapshot_dir, "b", on_date="2024-03-01")
    record_activity(snapshot_dir, "b", on_date="2024-03-02")
    ra = compute_streak(snapshot_dir, "a")
    rb = compute_streak(snapshot_dir, "b")
    assert ra.longest_streak == 1
    assert rb.longest_streak == 2
