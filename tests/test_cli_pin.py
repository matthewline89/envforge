"""CLI integration tests for the pin command group."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_pin import pin_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envforge"
    d.mkdir()
    return d


def test_set_cmd_prints_confirmation(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(pin_group, ["set", "stable", "snap_001", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "stable" in result.output
    assert "snap_001" in result.output


def test_list_cmd_shows_no_pins_message(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(pin_group, ["list", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No pins" in result.output


def test_list_cmd_shows_pins(runner: CliRunner, snap_dir: Path) -> None:
    runner.invoke(pin_group, ["set", "prod", "snap_prod", "--dir", str(snap_dir)])
    result = runner.invoke(pin_group, ["list", "--dir", str(snap_dir)])
    assert "prod" in result.output
    assert "snap_prod" in result.output


def test_resolve_cmd_prints_snapshot_name(runner: CliRunner, snap_dir: Path) -> None:
    runner.invoke(pin_group, ["set", "stable", "snap_42", "--dir", str(snap_dir)])
    result = runner.invoke(pin_group, ["resolve", "stable", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "snap_42" in result.output


def test_resolve_cmd_exits_nonzero_for_missing(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(pin_group, ["resolve", "ghost", "--dir", str(snap_dir)])
    assert result.exit_code != 0


def test_remove_cmd_succeeds(runner: CliRunner, snap_dir: Path) -> None:
    runner.invoke(pin_group, ["set", "old", "snap_old", "--dir", str(snap_dir)])
    result = runner.invoke(pin_group, ["remove", "old", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "old" in result.output


def test_remove_cmd_exits_nonzero_when_missing(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(pin_group, ["remove", "nope", "--dir", str(snap_dir)])
    assert result.exit_code != 0
