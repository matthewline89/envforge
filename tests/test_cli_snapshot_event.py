"""Tests for envforge.cli_snapshot_event."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_snapshot_event import event_group
from envforge.snapshot_event import record_event


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_record_cmd_prints_confirmation(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(
        event_group, ["record", "snap1", "deployed", "--dir", str(snap_dir)]
    )
    assert result.exit_code == 0
    assert "deployed" in result.output
    assert "snap1" in result.output


def test_record_cmd_stores_user(runner: CliRunner, snap_dir: Path) -> None:
    runner.invoke(
        event_group,
        ["record", "snap1", "created", "--user", "bob", "--dir", str(snap_dir)],
    )
    from envforge.snapshot_event import get_event_log

    log = get_event_log(snap_dir)
    assert log.entries[0].user == "bob"


def test_log_cmd_shows_events(runner: CliRunner, snap_dir: Path) -> None:
    record_event(snap_dir, "snap1", "updated", note="patch")
    result = runner.invoke(event_group, ["log", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "updated" in result.output


def test_log_cmd_no_events_message(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(event_group, ["log", "ghost", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No events" in result.output


def test_clear_cmd_removes_events(runner: CliRunner, snap_dir: Path) -> None:
    record_event(snap_dir, "snap1", "created")
    result = runner.invoke(event_group, ["clear", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "1" in result.output


def test_clear_cmd_zero_when_none(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(event_group, ["clear", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "0" in result.output
