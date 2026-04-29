"""Tests for envforge.cli_watch."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from envforge.cli_watch import watch_group
from envforge.watch import WatchSession


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def snap_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snaps"
    d.mkdir()
    return d


def test_start_cmd_invokes_start_watch(runner: CliRunner, snap_dir: Path) -> None:
    mock_session = WatchSession()
    with patch("envforge.cli_watch.start_watch", return_value=mock_session) as mock_sw:
        result = runner.invoke(
            watch_group,
            ["start", "--dir", str(snap_dir), "--count", "1"],
        )
    assert result.exit_code == 0
    mock_sw.assert_called_once()


def test_start_cmd_prints_no_changes_message(runner: CliRunner, snap_dir: Path) -> None:
    mock_session = WatchSession()
    with patch("envforge.cli_watch.start_watch", return_value=mock_session):
        result = runner.invoke(
            watch_group,
            ["start", "--dir", str(snap_dir), "--count", "1"],
        )
    assert "No changes" in result.output


def test_start_cmd_creates_snapshot_dir(runner: CliRunner, tmp_path: Path) -> None:
    new_dir = tmp_path / "brand_new"
    assert not new_dir.exists()
    mock_session = WatchSession()
    with patch("envforge.cli_watch.start_watch", return_value=mock_session):
        runner.invoke(
            watch_group,
            ["start", "--dir", str(new_dir), "--count", "1"],
        )
    assert new_dir.exists()


def test_start_cmd_passes_interval(runner: CliRunner, snap_dir: Path) -> None:
    mock_session = WatchSession()
    with patch("envforge.cli_watch.start_watch", return_value=mock_session) as mock_sw:
        runner.invoke(
            watch_group,
            ["start", "--dir", str(snap_dir), "--interval", "2.5", "--count", "1"],
        )
    _, kwargs = mock_sw.call_args
    assert kwargs.get("interval") == 2.5 or mock_sw.call_args[0][1] == 2.5


def test_start_cmd_handles_keyboard_interrupt(runner: CliRunner, snap_dir: Path) -> None:
    with patch("envforge.cli_watch.start_watch", side_effect=KeyboardInterrupt):
        result = runner.invoke(
            watch_group,
            ["start", "--dir", str(snap_dir), "--count", "0"],
        )
    assert result.exit_code == 0
    assert "stopped" in result.output.lower()
