"""Tests for envforge.annotate."""

from __future__ import annotations

from pathlib import Path

import pytest

from envforge.annotate import (
    _annotations_path,
    get_annotation,
    list_annotations,
    remove_annotation,
    set_annotation,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def test_set_annotation_creates_file(snapshot_dir: Path) -> None:
    set_annotation(snapshot_dir, "dev", "development snapshot")
    assert _annotations_path(snapshot_dir).exists()


def test_set_annotation_stores_note(snapshot_dir: Path) -> None:
    set_annotation(snapshot_dir, "dev", "my note")
    assert get_annotation(snapshot_dir, "dev") == "my note"


def test_set_annotation_overwrites_existing(snapshot_dir: Path) -> None:
    set_annotation(snapshot_dir, "dev", "first")
    set_annotation(snapshot_dir, "dev", "second")
    assert get_annotation(snapshot_dir, "dev") == "second"


def test_get_annotation_returns_none_when_missing(snapshot_dir: Path) -> None:
    assert get_annotation(snapshot_dir, "ghost") is None


def test_get_annotation_returns_none_when_no_file(snapshot_dir: Path) -> None:
    assert get_annotation(snapshot_dir, "any") is None


def test_remove_annotation_returns_true_when_found(snapshot_dir: Path) -> None:
    set_annotation(snapshot_dir, "dev", "note")
    assert remove_annotation(snapshot_dir, "dev") is True


def test_remove_annotation_returns_false_when_missing(snapshot_dir: Path) -> None:
    assert remove_annotation(snapshot_dir, "ghost") is False


def test_remove_annotation_deletes_entry(snapshot_dir: Path) -> None:
    set_annotation(snapshot_dir, "dev", "note")
    remove_annotation(snapshot_dir, "dev")
    assert get_annotation(snapshot_dir, "dev") is None


def test_list_annotations_returns_all(snapshot_dir: Path) -> None:
    set_annotation(snapshot_dir, "dev", "note-a")
    set_annotation(snapshot_dir, "prod", "note-b")
    result = list_annotations(snapshot_dir)
    assert result == {"dev": "note-a", "prod": "note-b"}


def test_list_annotations_empty_when_no_file(snapshot_dir: Path) -> None:
    assert list_annotations(snapshot_dir) == {}
