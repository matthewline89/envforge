"""Tests for envforge.note."""
import pytest
from pathlib import Path
from envforge.note import set_note, get_note, remove_note, list_notes


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def test_set_note_creates_notes_file(snapshot_dir):
    set_note(snapshot_dir, "dev", "development environment")
    assert (snapshot_dir / "notes.json").exists()


def test_set_note_stores_text(snapshot_dir):
    set_note(snapshot_dir, "dev", "development environment")
    assert get_note(snapshot_dir, "dev") == "development environment"


def test_set_note_returns_true_when_new(snapshot_dir):
    result = set_note(snapshot_dir, "dev", "first note")
    assert result is True


def test_set_note_returns_false_when_updated(snapshot_dir):
    set_note(snapshot_dir, "dev", "first note")
    result = set_note(snapshot_dir, "dev", "updated note")
    assert result is False


def test_set_note_overwrites_existing(snapshot_dir):
    set_note(snapshot_dir, "dev", "old text")
    set_note(snapshot_dir, "dev", "new text")
    assert get_note(snapshot_dir, "dev") == "new text"


def test_get_note_returns_none_when_missing(snapshot_dir):
    assert get_note(snapshot_dir, "nonexistent") is None


def test_get_note_returns_none_before_any_notes(snapshot_dir):
    assert get_note(snapshot_dir, "dev") is None


def test_remove_note_returns_true_when_found(snapshot_dir):
    set_note(snapshot_dir, "dev", "some note")
    assert remove_note(snapshot_dir, "dev") is True


def test_remove_note_returns_false_when_missing(snapshot_dir):
    assert remove_note(snapshot_dir, "ghost") is False


def test_remove_note_deletes_entry(snapshot_dir):
    set_note(snapshot_dir, "dev", "some note")
    remove_note(snapshot_dir, "dev")
    assert get_note(snapshot_dir, "dev") is None


def test_list_notes_returns_all_entries(snapshot_dir):
    set_note(snapshot_dir, "dev", "dev note")
    set_note(snapshot_dir, "prod", "prod note")
    result = list_notes(snapshot_dir)
    assert result == {"dev": "dev note", "prod": "prod note"}


def test_list_notes_returns_empty_dict_when_none(snapshot_dir):
    assert list_notes(snapshot_dir) == {}


def test_multiple_snapshots_independent(snapshot_dir):
    set_note(snapshot_dir, "a", "note a")
    set_note(snapshot_dir, "b", "note b")
    remove_note(snapshot_dir, "a")
    assert get_note(snapshot_dir, "b") == "note b"
    assert get_note(snapshot_dir, "a") is None
