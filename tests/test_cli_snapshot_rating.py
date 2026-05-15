"""Tests for envforge.cli_snapshot_rating."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_snapshot_rating import rating_group
from envforge.snapshot_rating import set_rating


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_set_cmd_prints_rated(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(rating_group, ["set", "snap1", "4", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "Rated" in result.output
    assert "snap1" in result.output


def test_set_cmd_prints_updated_on_overwrite(runner: CliRunner, snap_dir: Path) -> None:
    set_rating(snap_dir, "snap1", 3)
    result = runner.invoke(rating_group, ["set", "snap1", "5", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "Updated" in result.output


def test_set_cmd_fails_for_invalid_stars(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(rating_group, ["set", "snap1", "9", "--dir", str(snap_dir)])
    assert result.exit_code != 0


def test_remove_cmd_prints_removed(runner: CliRunner, snap_dir: Path) -> None:
    set_rating(snap_dir, "snap1", 2)
    result = runner.invoke(rating_group, ["remove", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_cmd_prints_not_found(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(rating_group, ["remove", "ghost", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No rating" in result.output


def test_show_cmd_prints_stars(runner: CliRunner, snap_dir: Path) -> None:
    set_rating(snap_dir, "snap1", 4)
    result = runner.invoke(rating_group, ["show", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "4/5" in result.output


def test_show_cmd_prints_no_rating(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(rating_group, ["show", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No rating" in result.output


def test_list_cmd_shows_no_ratings_message(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(rating_group, ["list", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No ratings" in result.output


def test_list_cmd_shows_entries(runner: CliRunner, snap_dir: Path) -> None:
    set_rating(snap_dir, "snap1", 3)
    result = runner.invoke(rating_group, ["list", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "snap1" in result.output


def test_top_cmd_shows_top_entries(runner: CliRunner, snap_dir: Path) -> None:
    set_rating(snap_dir, "a", 5)
    set_rating(snap_dir, "b", 1)
    result = runner.invoke(rating_group, ["top", "--limit", "1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "a" in result.output
    assert "b" not in result.output
