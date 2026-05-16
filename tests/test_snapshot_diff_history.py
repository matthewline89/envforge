"""Tests for envforge.snapshot_diff_history."""
import json
import pytest
from pathlib import Path

from envforge.snapshot_diff_history import (
    record_diff,
    get_diff_history,
    clear_diff_history,
    DiffHistoryEntry,
    DiffHistory,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snaps"
    d.mkdir()
    return d


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


def test_record_diff_creates_history_file(snapshot_dir):
    _write(snapshot_dir, "a", {"X": "1"})
    _write(snapshot_dir, "b", {"X": "1", "Y": "2"})
    record_diff(snapshot_dir, "a", "b")
    assert (snapshot_dir / "diff_history.json").exists()


def test_record_diff_returns_entry(snapshot_dir):
    _write(snapshot_dir, "a", {"X": "1"})
    _write(snapshot_dir, "b", {"X": "2"})
    entry = record_diff(snapshot_dir, "a", "b")
    assert isinstance(entry, DiffHistoryEntry)
    assert entry.snapshot_a == "a"
    assert entry.snapshot_b == "b"


def test_record_diff_captures_added(snapshot_dir):
    _write(snapshot_dir, "a", {})
    _write(snapshot_dir, "b", {"NEW": "val"})
    entry = record_diff(snapshot_dir, "a", "b")
    assert "NEW" in entry.added


def test_record_diff_captures_removed(snapshot_dir):
    _write(snapshot_dir, "a", {"OLD": "val"})
    _write(snapshot_dir, "b", {})
    entry = record_diff(snapshot_dir, "a", "b")
    assert "OLD" in entry.removed


def test_record_diff_captures_changed(snapshot_dir):
    _write(snapshot_dir, "a", {"K": "v1"})
    _write(snapshot_dir, "b", {"K": "v2"})
    entry = record_diff(snapshot_dir, "a", "b")
    assert "K" in entry.changed


def test_record_diff_stores_note(snapshot_dir):
    _write(snapshot_dir, "a", {})
    _write(snapshot_dir, "b", {})
    entry = record_diff(snapshot_dir, "a", "b", note="weekly check")
    assert entry.note == "weekly check"


def test_record_diff_increments_id(snapshot_dir):
    _write(snapshot_dir, "a", {})
    _write(snapshot_dir, "b", {})
    e1 = record_diff(snapshot_dir, "a", "b")
    e2 = record_diff(snapshot_dir, "a", "b")
    assert e2.id == e1.id + 1


def test_get_diff_history_returns_all(snapshot_dir):
    _write(snapshot_dir, "a", {})
    _write(snapshot_dir, "b", {})
    record_diff(snapshot_dir, "a", "b")
    record_diff(snapshot_dir, "a", "b")
    history = get_diff_history(snapshot_dir)
    assert isinstance(history, DiffHistory)
    assert len(history) == 2


def test_get_diff_history_filters_by_snapshot(snapshot_dir):
    _write(snapshot_dir, "a", {})
    _write(snapshot_dir, "b", {})
    _write(snapshot_dir, "c", {})
    record_diff(snapshot_dir, "a", "b")
    record_diff(snapshot_dir, "b", "c")
    record_diff(snapshot_dir, "a", "c")
    history = get_diff_history(snapshot_dir, snapshot_name="b")
    assert len(history) == 2


def test_get_diff_history_empty_when_no_file(snapshot_dir):
    history = get_diff_history(snapshot_dir)
    assert history.is_empty()


def test_clear_diff_history_returns_count(snapshot_dir):
    _write(snapshot_dir, "a", {})
    _write(snapshot_dir, "b", {})
    record_diff(snapshot_dir, "a", "b")
    record_diff(snapshot_dir, "a", "b")
    removed = clear_diff_history(snapshot_dir)
    assert removed == 2


def test_clear_diff_history_empties_file(snapshot_dir):
    _write(snapshot_dir, "a", {})
    _write(snapshot_dir, "b", {})
    record_diff(snapshot_dir, "a", "b")
    clear_diff_history(snapshot_dir)
    history = get_diff_history(snapshot_dir)
    assert history.is_empty()
