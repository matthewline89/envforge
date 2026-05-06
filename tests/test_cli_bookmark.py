"""Tests for envforge.cli_bookmark."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.bookmark import set_bookmark
from envforge.cli_bookmark import bookmark_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_set_cmd_prints_created(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(
        bookmark_group, ["set", "prod", "production-snap", "--dir", str(snap_dir)]
    )
    assert result.exit_code == 0
    assert "created" in result.output


def test_set_cmd_prints_updated_on_overwrite(runner: CliRunner, snap_dir: Path) -> None:
    set_bookmark(snap_dir, "prod", "old-snap")
    result = runner.invoke(
        bookmark_group, ["set", "prod", "new-snap", "--dir", str(snap_dir)]
    )
    assert result.exit_code == 0
    assert "updated" in result.output


def test_remove_cmd_prints_removed(runner: CliRunner, snap_dir: Path) -> None:
    set_bookmark(snap_dir, "dev", "dev-snap")
    result = runner.invoke(bookmark_group, ["remove", "dev", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_cmd_prints_not_found(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(
        bookmark_group, ["remove", "ghost", "--dir", str(snap_dir)]
    )
    assert "not found" in result.output


def test_list_cmd_shows_no_bookmarks_message(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(bookmark_group, ["list", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No bookmarks" in result.output


def test_list_cmd_shows_bookmarks(runner: CliRunner, snap_dir: Path) -> None:
    set_bookmark(snap_dir, "alpha", "snap-alpha")
    set_bookmark(snap_dir, "beta", "snap-beta")
    result = runner.invoke(bookmark_group, ["list", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "snap-alpha" in result.output


def test_resolve_cmd_prints_snapshot_name(runner: CliRunner, snap_dir: Path) -> None:
    set_bookmark(snap_dir, "main", "main-env-snap")
    result = runner.invoke(bookmark_group, ["resolve", "main", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "main-env-snap" in result.output


def test_resolve_cmd_missing_bookmark(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(
        bookmark_group, ["resolve", "missing", "--dir", str(snap_dir)]
    )
    assert "not found" in result.output
