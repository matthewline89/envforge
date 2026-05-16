"""Tests for envforge.cli_snapshot_diff_history."""
import json
import pytest
from pathlib import Path
from click.testing import CliRunner

from envforge.cli_snapshot_diff_history import diff_history_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def snap_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snaps"
    d.mkdir()
    return d


def _write(snap_dir: Path, name: str, env: dict) -> None:
    (snap_dir / f"{name}.json").write_text(json.dumps(env))


def test_record_cmd_prints_confirmation(runner, snap_dir):
    _write(snap_dir, "a", {"X": "1"})
    _write(snap_dir, "b", {"X": "1", "Y": "2"})
    result = runner.invoke(diff_history_group, ["record", "a", "b", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "Recorded diff #1" in result.output
    assert "a -> b" in result.output


def test_record_cmd_shows_counts(runner, snap_dir):
    _write(snap_dir, "a", {})
    _write(snap_dir, "b", {"K": "v"})
    result = runner.invoke(diff_history_group, ["record", "a", "b", "--dir", str(snap_dir)])
    assert "Added: 1" in result.output


def test_record_cmd_with_note(runner, snap_dir):
    _write(snap_dir, "a", {})
    _write(snap_dir, "b", {})
    result = runner.invoke(
        diff_history_group,
        ["record", "a", "b", "--note", "ci run", "--dir", str(snap_dir)],
    )
    assert result.exit_code == 0


def test_log_cmd_shows_no_history_message(runner, snap_dir):
    result = runner.invoke(diff_history_group, ["log", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No diff history found" in result.output


def test_log_cmd_lists_entries(runner, snap_dir):
    _write(snap_dir, "a", {})
    _write(snap_dir, "b", {"K": "v"})
    runner.invoke(diff_history_group, ["record", "a", "b", "--dir", str(snap_dir)])
    result = runner.invoke(diff_history_group, ["log", "--dir", str(snap_dir)])
    assert "#1" in result.output
    assert "a -> b" in result.output


def test_log_cmd_filter_by_snapshot(runner, snap_dir):
    _write(snap_dir, "a", {})
    _write(snap_dir, "b", {})
    _write(snap_dir, "c", {})
    runner.invoke(diff_history_group, ["record", "a", "b", "--dir", str(snap_dir)])
    runner.invoke(diff_history_group, ["record", "b", "c", "--dir", str(snap_dir)])
    runner.invoke(diff_history_group, ["record", "a", "c", "--dir", str(snap_dir)])
    result = runner.invoke(diff_history_group, ["log", "--snapshot", "b", "--dir", str(snap_dir)])
    assert "#1" in result.output
    assert "#2" in result.output
    assert "#3" not in result.output


def test_clear_cmd_reports_removed(runner, snap_dir):
    _write(snap_dir, "a", {})
    _write(snap_dir, "b", {})
    runner.invoke(diff_history_group, ["record", "a", "b", "--dir", str(snap_dir)])
    result = runner.invoke(
        diff_history_group, ["clear", "--dir", str(snap_dir)], input="y\n"
    )
    assert result.exit_code == 0
    assert "Cleared 1" in result.output
