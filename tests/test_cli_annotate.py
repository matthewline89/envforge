"""Tests for envforge.cli_annotate."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_annotate import annotate_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def test_set_cmd_prints_confirmation(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(annotate_group, ["set", "dev", "my note", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "Annotation set for 'dev'" in result.output


def test_show_cmd_prints_note(runner: CliRunner, snap_dir: Path) -> None:
    runner.invoke(annotate_group, ["set", "dev", "hello world", "--dir", str(snap_dir)])
    result = runner.invoke(annotate_group, ["show", "dev", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "hello world" in result.output


def test_show_cmd_missing_note(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(annotate_group, ["show", "ghost", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No annotation" in result.output


def test_remove_cmd_prints_removed(runner: CliRunner, snap_dir: Path) -> None:
    runner.invoke(annotate_group, ["set", "dev", "note", "--dir", str(snap_dir)])
    result = runner.invoke(annotate_group, ["remove", "dev", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_cmd_not_found(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(annotate_group, ["remove", "ghost", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No annotation found" in result.output


def test_list_cmd_shows_no_annotations_message(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(annotate_group, ["list", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No annotations found" in result.output


def test_list_cmd_shows_annotations(runner: CliRunner, snap_dir: Path) -> None:
    runner.invoke(annotate_group, ["set", "dev", "dev note", "--dir", str(snap_dir)])
    runner.invoke(annotate_group, ["set", "prod", "prod note", "--dir", str(snap_dir)])
    result = runner.invoke(annotate_group, ["list", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output
