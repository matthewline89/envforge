"""Tests for envforge.cli_slot."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_slot import slot_group
from envforge.slot import set_slot


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_set_cmd_prints_created(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(slot_group, ["set", "current", "snap_v1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "Created" in result.output
    assert "current" in result.output


def test_set_cmd_prints_updated_on_overwrite(runner: CliRunner, snap_dir: Path) -> None:
    set_slot(snap_dir, "current", "snap_v1")
    result = runner.invoke(slot_group, ["set", "current", "snap_v2", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "Updated" in result.output


def test_remove_cmd_prints_removed(runner: CliRunner, snap_dir: Path) -> None:
    set_slot(snap_dir, "staging", "snap_s")
    result = runner.invoke(slot_group, ["remove", "staging", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_cmd_missing_slot(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(slot_group, ["remove", "ghost", "--dir", str(snap_dir)])
    assert "not found" in result.output


def test_resolve_cmd_prints_snapshot_name(runner: CliRunner, snap_dir: Path) -> None:
    set_slot(snap_dir, "prod", "snap_prod")
    result = runner.invoke(slot_group, ["resolve", "prod", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "snap_prod" in result.output


def test_resolve_cmd_missing_slot(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(slot_group, ["resolve", "missing", "--dir", str(snap_dir)])
    assert "No snapshot" in result.output


def test_list_cmd_shows_no_slots_message(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(slot_group, ["list", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No slots" in result.output


def test_list_cmd_shows_slots(runner: CliRunner, snap_dir: Path) -> None:
    set_slot(snap_dir, "dev", "snap_dev")
    set_slot(snap_dir, "prod", "snap_prod")
    result = runner.invoke(slot_group, ["list", "--dir", str(snap_dir)])
    assert "dev" in result.output
    assert "snap_dev" in result.output
    assert "prod" in result.output
