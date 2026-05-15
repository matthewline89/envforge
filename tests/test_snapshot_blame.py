"""Tests for envforge.snapshot_blame."""
from __future__ import annotations

import pytest
from pathlib import Path

from envforge.snapshot_blame import (
    BlameEntry,
    BlameReport,
    clear_blame,
    get_blame,
    record_blame,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envforge"
    d.mkdir()
    return d


def test_record_blame_creates_blame_file(snapshot_dir: Path) -> None:
    record_blame(snapshot_dir, "snap1", "KEY", "val", "alice", "2024-01-01T00:00:00+00:00")
    assert (snapshot_dir / "blame.json").exists()


def test_record_blame_returns_entry(snapshot_dir: Path) -> None:
    entry = record_blame(snapshot_dir, "snap1", "KEY", "val", "bob", "2024-01-01T00:00:00+00:00")
    assert isinstance(entry, BlameEntry)
    assert entry.key == "KEY"
    assert entry.user == "bob"


def test_record_blame_stores_note(snapshot_dir: Path) -> None:
    entry = record_blame(
        snapshot_dir, "snap1", "KEY", "val", "carol", "2024-01-01T00:00:00+00:00", note="initial"
    )
    assert entry.note == "initial"


def test_get_blame_returns_blame_report(snapshot_dir: Path) -> None:
    record_blame(snapshot_dir, "snap1", "FOO", "bar", "alice", "2024-01-01T00:00:00+00:00")
    report = get_blame(snapshot_dir, "snap1")
    assert isinstance(report, BlameReport)
    assert report.snapshot_name == "snap1"


def test_get_blame_returns_all_entries(snapshot_dir: Path) -> None:
    record_blame(snapshot_dir, "snap1", "A", "1", "alice", "2024-01-01T00:00:00+00:00")
    record_blame(snapshot_dir, "snap1", "B", "2", "bob", "2024-01-02T00:00:00+00:00")
    report = get_blame(snapshot_dir, "snap1")
    assert len(report.entries) == 2


def test_get_blame_for_key_returns_correct_entry(snapshot_dir: Path) -> None:
    record_blame(snapshot_dir, "snap1", "MY_KEY", "my_val", "dave", "2024-01-01T00:00:00+00:00")
    report = get_blame(snapshot_dir, "snap1")
    entry = report.for_key("MY_KEY")
    assert entry is not None
    assert entry.value == "my_val"


def test_get_blame_for_missing_key_returns_none(snapshot_dir: Path) -> None:
    record_blame(snapshot_dir, "snap1", "X", "1", "alice", "2024-01-01T00:00:00+00:00")
    report = get_blame(snapshot_dir, "snap1")
    assert report.for_key("MISSING") is None


def test_get_blame_users_deduplicates(snapshot_dir: Path) -> None:
    record_blame(snapshot_dir, "snap1", "A", "1", "alice", "2024-01-01T00:00:00+00:00")
    record_blame(snapshot_dir, "snap1", "B", "2", "alice", "2024-01-02T00:00:00+00:00")
    report = get_blame(snapshot_dir, "snap1")
    assert report.users() == ["alice"]


def test_get_blame_empty_when_no_records(snapshot_dir: Path) -> None:
    report = get_blame(snapshot_dir, "nonexistent")
    assert report.entries == []


def test_clear_blame_returns_true_when_found(snapshot_dir: Path) -> None:
    record_blame(snapshot_dir, "snap1", "K", "v", "alice", "2024-01-01T00:00:00+00:00")
    assert clear_blame(snapshot_dir, "snap1") is True


def test_clear_blame_returns_false_when_not_found(snapshot_dir: Path) -> None:
    assert clear_blame(snapshot_dir, "ghost") is False


def test_clear_blame_removes_entries(snapshot_dir: Path) -> None:
    record_blame(snapshot_dir, "snap1", "K", "v", "alice", "2024-01-01T00:00:00+00:00")
    clear_blame(snapshot_dir, "snap1")
    report = get_blame(snapshot_dir, "snap1")
    assert report.entries == []


def test_blame_isolated_per_snapshot(snapshot_dir: Path) -> None:
    record_blame(snapshot_dir, "snap1", "K", "v", "alice", "2024-01-01T00:00:00+00:00")
    report2 = get_blame(snapshot_dir, "snap2")
    assert report2.entries == []
