"""Tests for envforge.cli_compare CLI commands."""

from __future__ import annotations

import json
import pathlib

import pytest
from click.testing import CliRunner

from envforge.cli_compare import run_cmd


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path


def _write(directory: pathlib.Path, name: str, data: dict) -> None:
    (directory / f"{name}.json").write_text(json.dumps(data))


def test_run_requires_two_snapshots(runner, snap_dir):
    _write(snap_dir, "a", {"K": "v"})
    result = runner.invoke(run_cmd, ["a", "--snapshot-dir", str(snap_dir)])
    assert result.exit_code != 0


def test_run_shows_keys(runner, snap_dir):
    _write(snap_dir, "a", {"KEY": "val1"})
    _write(snap_dir, "b", {"KEY": "val2"})
    result = runner.invoke(run_cmd, ["a", "b", "--snapshot-dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "KEY" in result.output


def test_run_shows_both_values(runner, snap_dir):
    _write(snap_dir, "a", {"ENV": "dev"})
    _write(snap_dir, "b", {"ENV": "prod"})
    result = runner.invoke(run_cmd, ["a", "b", "--snapshot-dir", str(snap_dir)])
    assert "dev" in result.output
    assert "prod" in result.output


def test_run_only_diff_hides_identical_keys(runner, snap_dir):
    _write(snap_dir, "a", {"SAME": "x", "DIFF": "1"})
    _write(snap_dir, "b", {"SAME": "x", "DIFF": "2"})
    result = runner.invoke(
        run_cmd, ["a", "b", "--only-diff", "--snapshot-dir", str(snap_dir)]
    )
    assert result.exit_code == 0
    assert "DIFF" in result.output
    assert "SAME" not in result.output


def test_run_no_differences_message(runner, snap_dir):
    data = {"K": "v"}
    _write(snap_dir, "a", data)
    _write(snap_dir, "b", data)
    result = runner.invoke(
        run_cmd, ["a", "b", "--only-diff", "--snapshot-dir", str(snap_dir)]
    )
    assert result.exit_code == 0
    assert "No differences" in result.output


def test_run_missing_snapshot_exits_with_error(runner, snap_dir):
    _write(snap_dir, "a", {"K": "v"})
    result = runner.invoke(run_cmd, ["a", "ghost", "--snapshot-dir", str(snap_dir)])
    assert result.exit_code != 0


def test_run_summary_footer_present(runner, snap_dir):
    _write(snap_dir, "a", {"K": "v"})
    _write(snap_dir, "b", {"K": "v"})
    result = runner.invoke(run_cmd, ["a", "b", "--snapshot-dir", str(snap_dir)])
    assert "Common keys" in result.output
    assert "Total" in result.output
