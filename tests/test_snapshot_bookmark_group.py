"""Tests for snapshot_bookmark_group."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_bookmark_group import build_report, BookmarkGroupReport


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envforge"
    d.mkdir()
    return d


def _write_bookmarks(d: Path, data: dict) -> None:
    (d / "bookmarks.json").write_text(json.dumps(data))


def _write_groups(d: Path, data: dict) -> None:
    (d / "groups.json").write_text(json.dumps(data))


def test_build_report_returns_bookmark_group_report(snapshot_dir):
    report = build_report(snapshot_dir)
    assert isinstance(report, BookmarkGroupReport)


def test_report_is_empty_when_no_bookmarks(snapshot_dir):
    report = build_report(snapshot_dir)
    assert report.is_empty()


def test_report_entry_count_matches_bookmarks(snapshot_dir):
    _write_bookmarks(snapshot_dir, {"prod": "snap_prod", "dev": "snap_dev"})
    report = build_report(snapshot_dir)
    assert len(report.entries) == 2


def test_report_entry_has_correct_snapshot(snapshot_dir):
    _write_bookmarks(snapshot_dir, {"prod": "snap_prod"})
    report = build_report(snapshot_dir)
    entry = report.for_bookmark("prod")
    assert entry is not None
    assert entry.snapshot == "snap_prod"


def test_report_entry_groups_empty_when_no_groups(snapshot_dir):
    _write_bookmarks(snapshot_dir, {"prod": "snap_prod"})
    report = build_report(snapshot_dir)
    entry = report.for_bookmark("prod")
    assert entry.groups == []


def test_report_entry_groups_populated(snapshot_dir):
    _write_bookmarks(snapshot_dir, {"prod": "snap_prod"})
    _write_groups(snapshot_dir, {"team-a": ["snap_prod"], "team-b": ["snap_prod"]})
    report = build_report(snapshot_dir)
    entry = report.for_bookmark("prod")
    assert "team-a" in entry.groups
    assert "team-b" in entry.groups


def test_for_bookmark_returns_none_for_missing(snapshot_dir):
    report = build_report(snapshot_dir)
    assert report.for_bookmark("missing") is None


def test_bookmarks_in_group_returns_matching(snapshot_dir):
    _write_bookmarks(snapshot_dir, {"prod": "snap_prod", "dev": "snap_dev"})
    _write_groups(snapshot_dir, {"backend": ["snap_prod"]})
    report = build_report(snapshot_dir)
    result = report.bookmarks_in_group("backend")
    assert "prod" in result
    assert "dev" not in result


def test_bookmarks_in_group_empty_for_unknown_group(snapshot_dir):
    _write_bookmarks(snapshot_dir, {"prod": "snap_prod"})
    report = build_report(snapshot_dir)
    assert report.bookmarks_in_group("nonexistent") == []


def test_groups_sorted_alphabetically(snapshot_dir):
    _write_bookmarks(snapshot_dir, {"prod": "snap_prod"})
    _write_groups(snapshot_dir, {"z-group": ["snap_prod"], "a-group": ["snap_prod"]})
    report = build_report(snapshot_dir)
    entry = report.for_bookmark("prod")
    assert entry.groups == ["a-group", "z-group"]
