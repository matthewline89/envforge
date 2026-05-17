"""Tests for envforge.cli_snapshot_flag."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_snapshot_flag import flag_group
from envforge.snapshot_flag import set_flag


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_set_cmd_prints_set(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(flag_group, ["set", "snap1", "important", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "set" in result.output


def test_set_cmd_prints_already_set(runner: CliRunner, snap_dir: Path) -> None:
    set_flag(snap_dir, "snap1", "important")
    result = runner.invoke(flag_group, ["set", "snap1", "important", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "already" in result.output


def test_remove_cmd_prints_removed(runner: CliRunner, snap_dir: Path) -> None:
    set_flag(snap_dir, "snap1", "temp")
    result = runner.invoke(flag_group, ["remove", "snap1", "temp", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_cmd_prints_not_found(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(flag_group, ["remove", "snap1", "ghost", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_show_cmd_lists_flags(runner: CliRunner, snap_dir: Path) -> None:
    set_flag(snap_dir, "snap1", "reviewed")
    set_flag(snap_dir, "snap1", "stable")
    result = runner.invoke(flag_group, ["show", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "reviewed" in result.output
    assert "stable" in result.output


def test_show_cmd_no_flags_message(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(flag_group, ["show", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No flags" in result.output


def test_find_cmd_shows_matching_snapshots(runner: CliRunner, snap_dir: Path) -> None:
    set_flag(snap_dir, "snap1", "reviewed")
    set_flag(snap_dir, "snap2", "reviewed")
    result = runner.invoke(flag_group, ["find", "reviewed", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "snap1" in result.output
    assert "snap2" in result.output


def test_find_cmd_no_match_message(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(flag_group, ["find", "nonexistent", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No snapshots" in result.output


def test_clear_cmd_reports_count(runner: CliRunner, snap_dir: Path) -> None:
    set_flag(snap_dir, "snap1", "a")
    set_flag(snap_dir, "snap1", "b")
    result = runner.invoke(flag_group, ["clear", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "2" in result.output
