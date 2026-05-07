"""Tests for envforge.cli_snapshot_filter."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_snapshot_filter import filter_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _write(snap_dir: Path, name: str, env: dict[str, str]) -> None:
    """Write a snapshot JSON file to *snap_dir* with the given *name* and *env* mapping."""
    (snap_dir / f"{name}.json").write_text(json.dumps(env))


def test_by_key_cmd_shows_matched_snapshot(runner: CliRunner, snap_dir: Path) -> None:
    _write(snap_dir, "prod", {"AWS_KEY": "abc"})
    result = runner.invoke(filter_group, ["by-key", "AWS_*", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_by_key_cmd_no_match_message(runner: CliRunner, snap_dir: Path) -> None:
    _write(snap_dir, "prod", {"HOME": "/home"})
    result = runner.invoke(filter_group, ["by-key", "AWS_*", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No snapshots matched" in result.output


def test_by_key_cmd_reports_counts(runner: CliRunner, snap_dir: Path) -> None:
    _write(snap_dir, "snap1", {"FOO": "1"})
    _write(snap_dir, "snap2", {"BAR": "2"})
    result = runner.invoke(filter_group, ["by-key", "FOO", "--dir", str(snap_dir)])
    assert "1/2" in result.output


def test_by_value_cmd_shows_matched_snapshot(runner: CliRunner, snap_dir: Path) -> None:
    _write(snap_dir, "dev", {"DB": "postgres://localhost"})
    result = runner.invoke(filter_group, ["by-value", "postgres*", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "dev" in result.output


def test_by_value_cmd_no_match_message(runner: CliRunner, snap_dir: Path) -> None:
    _write(snap_dir, "dev", {"DB": "sqlite:///db.sqlite3"})
    result = runner.invoke(filter_group, ["by-value", "postgres*", "--dir", str(snap_dir)])
    assert "No snapshots matched" in result.output


def test_by_size_cmd_min_filter(runner: CliRunner, snap_dir: Path) -> None:
    _write(snap_dir, "big", {"A": "1", "B": "2", "C": "3"})
    _write(snap_dir, "small", {"A": "1"})
    result = runner.invoke(filter_group, ["by-size", "--min", "2", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "big" in result.output
    assert "small" not in result.output


def test_by_size_cmd_no_match_message(runner: CliRunner, snap_dir: Path) -> None:
    _write(snap_dir, "tiny", {"A": "1"})
    result = runner.invoke(filter_group, ["by-size", "--min", "10", "--dir", str(snap_dir)])
    assert "No snapshots matched" in result.output


def test_by_size_cmd_max_filter(runner: CliRunner, snap_dir: Path) -> None:
    """Snapshots with more keys than --max should be excluded from results."""
    _write(snap_dir, "big", {"A": "1", "B": "2", "C": "3"})
    _write(snap_dir, "small", {"A": "1"})
    result = runner.invoke(filter_group, ["by-size", "--max", "2", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "small" in result.output
    assert "big" not in result.output
