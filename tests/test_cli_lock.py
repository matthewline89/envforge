"""Tests for envforge.cli_lock CLI commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_lock import lock_group
from envforge import lock as lock_mod


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_set_cmd_prints_locked_message(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(lock_group, ["set", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "locked" in result.output


def test_set_cmd_prints_already_locked_message(runner: CliRunner, snap_dir: Path) -> None:
    lock_mod.lock_snapshot(snap_dir, "snap1")
    result = runner.invoke(lock_group, ["set", "snap1", "--dir", str(snap_dir)])
    assert "already locked" in result.output


def test_unset_cmd_prints_unlocked_message(runner: CliRunner, snap_dir: Path) -> None:
    lock_mod.lock_snapshot(snap_dir, "snap1")
    result = runner.invoke(lock_group, ["unset", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "unlocked" in result.output


def test_unset_cmd_prints_not_locked_message(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(lock_group, ["unset", "snap1", "--dir", str(snap_dir)])
    assert "not locked" in result.output


def test_list_cmd_shows_no_locks_message(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(lock_group, ["list", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No snapshots" in result.output


def test_list_cmd_shows_locked_names(runner: CliRunner, snap_dir: Path) -> None:
    lock_mod.lock_snapshot(snap_dir, "alpha")
    lock_mod.lock_snapshot(snap_dir, "beta")
    result = runner.invoke(lock_group, ["list", "--dir", str(snap_dir)])
    assert "alpha" in result.output
    assert "beta" in result.output


def test_check_cmd_reports_locked(runner: CliRunner, snap_dir: Path) -> None:
    lock_mod.lock_snapshot(snap_dir, "snap1")
    result = runner.invoke(lock_group, ["check", "snap1", "--dir", str(snap_dir)])
    assert "is locked" in result.output


def test_check_cmd_reports_not_locked(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(lock_group, ["check", "snap1", "--dir", str(snap_dir)])
    assert "not locked" in result.output
