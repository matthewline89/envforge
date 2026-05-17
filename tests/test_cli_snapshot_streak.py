"""Tests for envforge.cli_snapshot_streak."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_snapshot_streak import streak_group
from envforge.snapshot_streak import record_activity


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_record_cmd_prints_confirmation(runner, snap_dir):
    result = runner.invoke(
        streak_group,
        ["record", "env1", "--date", "2024-05-01", "--dir", str(snap_dir)],
    )
    assert result.exit_code == 0
    assert "env1" in result.output
    assert "2024-05-01" in result.output


def test_record_cmd_creates_streaks_file(runner, snap_dir):
    runner.invoke(
        streak_group,
        ["record", "env1", "--date", "2024-05-01", "--dir", str(snap_dir)],
    )
    assert (snap_dir / "streaks.json").exists()


def test_show_cmd_no_activity_message(runner, snap_dir):
    result = runner.invoke(
        streak_group,
        ["show", "missing", "--dir", str(snap_dir)],
    )
    assert result.exit_code == 0
    assert "No activity" in result.output


def test_show_cmd_prints_streak_info(runner, snap_dir):
    record_activity(snap_dir, "env1", on_date="2024-05-01")
    record_activity(snap_dir, "env1", on_date="2024-05-02")
    result = runner.invoke(
        streak_group,
        ["show", "env1", "--dir", str(snap_dir)],
    )
    assert result.exit_code == 0
    assert "env1" in result.output
    assert "Longest streak" in result.output


def test_show_cmd_prints_days_active(runner, snap_dir):
    record_activity(snap_dir, "env1", on_date="2024-05-01")
    result = runner.invoke(
        streak_group,
        ["show", "env1", "--dir", str(snap_dir)],
    )
    assert "Days active" in result.output
    assert "1" in result.output
