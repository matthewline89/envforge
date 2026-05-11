"""Tests for envforge.cli_snapshot_score."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_snapshot_score import score_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _write(snap_dir: Path, name: str, env: dict) -> None:
    (snap_dir / f"{name}.json").write_text(json.dumps(env))


def test_show_cmd_prints_score(runner: CliRunner, snap_dir: Path) -> None:
    _write(snap_dir, "mysnap", {"MY_VAR": "hello"})
    result = runner.invoke(score_group, ["show", "mysnap", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "Score" in result.output


def test_show_cmd_prints_grade(runner: CliRunner, snap_dir: Path) -> None:
    _write(snap_dir, "mysnap", {"MY_VAR": "hello"})
    result = runner.invoke(score_group, ["show", "mysnap", "--dir", str(snap_dir)])
    assert "Grade" in result.output


def test_show_cmd_prints_name(runner: CliRunner, snap_dir: Path) -> None:
    _write(snap_dir, "mysnap", {"KEY": "val"})
    result = runner.invoke(score_group, ["show", "mysnap", "--dir", str(snap_dir)])
    assert "mysnap" in result.output


def test_rank_cmd_lists_snapshots(runner: CliRunner, snap_dir: Path) -> None:
    _write(snap_dir, "snap_a", {"MY_VAR": "1"})
    _write(snap_dir, "snap_b", {"OTHER": "2"})
    result = runner.invoke(score_group, ["rank", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "snap_a" in result.output
    assert "snap_b" in result.output


def test_rank_cmd_no_snapshots_message(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(score_group, ["rank", "--dir", str(snap_dir)])
    assert "No snapshots found" in result.output


def test_rank_cmd_shows_rank_column(runner: CliRunner, snap_dir: Path) -> None:
    _write(snap_dir, "snap_a", {"MY_VAR": "1"})
    result = runner.invoke(score_group, ["rank", "--dir", str(snap_dir)])
    assert "Rank" in result.output
