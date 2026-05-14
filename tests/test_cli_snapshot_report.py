"""Tests for envforge.cli_snapshot_report."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_snapshot_report import report_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(snap_dir: Path, name: str, env: dict) -> None:
    (snap_dir / f"{name}.json").write_text(json.dumps(env))


def test_show_cmd_no_snapshots_message(runner, snap_dir):
    result = runner.invoke(
        report_group, ["show", "--dir", str(snap_dir)]
    )
    assert result.exit_code == 0
    assert "No snapshots found" in result.output


def test_show_cmd_prints_report(runner, snap_dir):
    _write(snap_dir, "dev", {"DB_HOST": "localhost"})
    result = runner.invoke(
        report_group, ["show", "--dir", str(snap_dir)]
    )
    assert result.exit_code == 0
    assert "dev" in result.output


def test_show_cmd_accepts_specific_names(runner, snap_dir):
    _write(snap_dir, "dev", {"A": "1"})
    _write(snap_dir, "prod", {"B": "2"})
    result = runner.invoke(
        report_group, ["show", "dev", "--dir", str(snap_dir)]
    )
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" not in result.output


def test_show_cmd_contains_total_line(runner, snap_dir):
    _write(snap_dir, "s1", {"KEY": "val"})
    result = runner.invoke(
        report_group, ["show", "--dir", str(snap_dir)]
    )
    assert "Total:" in result.output


def test_summary_cmd_prints_counts(runner, snap_dir):
    _write(snap_dir, "a", {"X": "1"})
    _write(snap_dir, "b", {"Y": "2"})
    result = runner.invoke(
        report_group, ["summary", "--dir", str(snap_dir)]
    )
    assert result.exit_code == 0
    assert "Snapshots: 2" in result.output


def test_summary_cmd_shows_error_count(runner, snap_dir):
    _write(snap_dir, "ok", {"VALID": "val"})
    result = runner.invoke(
        report_group, ["summary", "--dir", str(snap_dir)]
    )
    assert "With errors:" in result.output


def test_summary_cmd_shows_expired_count(runner, snap_dir):
    _write(snap_dir, "fresh", {"K": "v"})
    result = runner.invoke(
        report_group, ["summary", "--dir", str(snap_dir)]
    )
    assert "Expired:" in result.output
