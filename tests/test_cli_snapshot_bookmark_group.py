"""Tests for cli_snapshot_bookmark_group."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_snapshot_bookmark_group import bookmark_group_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envforge"
    d.mkdir()
    return d


def _write(d: Path, name: str, data: dict) -> None:
    (d / name).write_text(json.dumps(data))


def test_report_cmd_no_bookmarks_message(runner, snap_dir):
    result = runner.invoke(bookmark_group_group, ["report", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No bookmarks found" in result.output


def test_report_cmd_shows_bookmark_and_snapshot(runner, snap_dir):
    _write(snap_dir, "bookmarks.json", {"prod": "snap_prod"})
    result = runner.invoke(bookmark_group_group, ["report", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "snap_prod" in result.output


def test_report_cmd_shows_none_when_no_groups(runner, snap_dir):
    _write(snap_dir, "bookmarks.json", {"prod": "snap_prod"})
    result = runner.invoke(bookmark_group_group, ["report", "--dir", str(snap_dir)])
    assert "(none)" in result.output


def test_report_cmd_shows_group_name(runner, snap_dir):
    _write(snap_dir, "bookmarks.json", {"prod": "snap_prod"})
    _write(snap_dir, "groups.json", {"backend": ["snap_prod"]})
    result = runner.invoke(bookmark_group_group, ["report", "--dir", str(snap_dir)])
    assert "backend" in result.output


def test_find_cmd_no_match_message(runner, snap_dir):
    result = runner.invoke(bookmark_group_group, ["find", "backend", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No bookmarks found" in result.output


def test_find_cmd_returns_matching_bookmark(runner, snap_dir):
    _write(snap_dir, "bookmarks.json", {"prod": "snap_prod"})
    _write(snap_dir, "groups.json", {"backend": ["snap_prod"]})
    result = runner.invoke(bookmark_group_group, ["find", "backend", "--dir", str(snap_dir)])
    assert "prod" in result.output


def test_show_cmd_not_found_message(runner, snap_dir):
    result = runner.invoke(bookmark_group_group, ["show", "missing", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_show_cmd_prints_snapshot(runner, snap_dir):
    _write(snap_dir, "bookmarks.json", {"prod": "snap_prod"})
    result = runner.invoke(bookmark_group_group, ["show", "prod", "--dir", str(snap_dir)])
    assert "snap_prod" in result.output


def test_show_cmd_prints_no_groups(runner, snap_dir):
    _write(snap_dir, "bookmarks.json", {"prod": "snap_prod"})
    result = runner.invoke(bookmark_group_group, ["show", "prod", "--dir", str(snap_dir)])
    assert "(no groups)" in result.output


def test_show_cmd_prints_group_names(runner, snap_dir):
    _write(snap_dir, "bookmarks.json", {"prod": "snap_prod"})
    _write(snap_dir, "groups.json", {"ops": ["snap_prod"]})
    result = runner.invoke(bookmark_group_group, ["show", "prod", "--dir", str(snap_dir)])
    assert "ops" in result.output
