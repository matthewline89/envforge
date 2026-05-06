"""Tests for envforge.cli_schedule."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envforge.cli_schedule import schedule_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snaps"
    d.mkdir()
    return d


def _fake_start_schedule(snapshot_dir, snapshot_name, interval_seconds,
                         max_runs=1, on_snapshot=None, env=None, _sleep=None):
    from envforge.schedule import ScheduleEntry, ScheduleSession
    entry = ScheduleEntry(
        snapshot_name=snapshot_name,
        interval_seconds=interval_seconds,
        run_count=max_runs,
        last_run="2024-01-01T00:00:00",
    )
    session = ScheduleSession(entries=[entry], stopped_at="2024-01-01T00:00:01")
    if on_snapshot:
        for i in range(max_runs):
            on_snapshot(f"{snapshot_name}_fake_{i}")
    return session


def test_run_cmd_prints_saved_snapshot(runner: CliRunner, snap_dir: Path) -> None:
    with patch("envforge.cli_schedule.start_schedule", side_effect=_fake_start_schedule):
        result = runner.invoke(
            schedule_group,
            ["run", "mysnap", "--runs", "1", "--dir", str(snap_dir)],
        )
    assert result.exit_code == 0
    assert "Snapshot saved" in result.output


def test_run_cmd_prints_completion_message(runner: CliRunner, snap_dir: Path) -> None:
    with patch("envforge.cli_schedule.start_schedule", side_effect=_fake_start_schedule):
        result = runner.invoke(
            schedule_group,
            ["run", "mysnap", "--runs", "2", "--dir", str(snap_dir)],
        )
    assert "Schedule complete" in result.output


def test_run_cmd_creates_snapshot_dir(runner: CliRunner, tmp_path: Path) -> None:
    new_dir = tmp_path / "new_snaps"
    with patch("envforge.cli_schedule.start_schedule", side_effect=_fake_start_schedule):
        runner.invoke(
            schedule_group,
            ["run", "s", "--dir", str(new_dir)],
        )
    assert new_dir.exists()


def test_run_cmd_default_runs_is_one(runner: CliRunner, snap_dir: Path) -> None:
    captured: list = []

    def _capture(*args, **kwargs):
        captured.append(kwargs.get("max_runs"))
        return _fake_start_schedule(*args, **kwargs)

    with patch("envforge.cli_schedule.start_schedule", side_effect=_capture):
        runner.invoke(schedule_group, ["run", "s", "--dir", str(snap_dir)])
    assert captured[0] == 1
