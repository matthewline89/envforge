"""CLI tests for envforge.cli_snapshot_meta."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_snapshot_meta import meta_group
from envforge.snapshot_meta import set_meta


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_set_cmd_prints_set(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(meta_group, ["set", "s1", "owner", "bob", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "Set" in result.output
    assert "owner" in result.output


def test_set_cmd_prints_updated(runner: CliRunner, snap_dir: Path) -> None:
    set_meta(snap_dir, "s1", "owner", "alice")
    result = runner.invoke(meta_group, ["set", "s1", "owner", "bob", "--dir", str(snap_dir)])
    assert "Updated" in result.output


def test_get_cmd_prints_value(runner: CliRunner, snap_dir: Path) -> None:
    set_meta(snap_dir, "s1", "env", "prod")
    result = runner.invoke(meta_group, ["get", "s1", "env", "--dir", str(snap_dir)])
    assert "prod" in result.output


def test_get_cmd_missing_key(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(meta_group, ["get", "s1", "missing", "--dir", str(snap_dir)])
    assert "No meta key" in result.output


def test_remove_cmd_prints_removed(runner: CliRunner, snap_dir: Path) -> None:
    set_meta(snap_dir, "s1", "k", "v")
    result = runner.invoke(meta_group, ["remove", "s1", "k", "--dir", str(snap_dir)])
    assert "Removed" in result.output


def test_remove_cmd_not_found(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(meta_group, ["remove", "s1", "nope", "--dir", str(snap_dir)])
    assert "not found" in result.output


def test_show_cmd_no_metadata(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(meta_group, ["show", "s1", "--dir", str(snap_dir)])
    assert "No metadata" in result.output


def test_show_cmd_prints_json(runner: CliRunner, snap_dir: Path) -> None:
    set_meta(snap_dir, "s1", "k", "v")
    result = runner.invoke(meta_group, ["show", "s1", "--dir", str(snap_dir)])
    data = json.loads(result.output)
    assert data["k"] == "v"


def test_list_cmd_no_snapshots(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(meta_group, ["list", "--dir", str(snap_dir)])
    assert "No snapshots" in result.output


def test_list_cmd_shows_names(runner: CliRunner, snap_dir: Path) -> None:
    set_meta(snap_dir, "alpha", "x", "1")
    set_meta(snap_dir, "beta", "y", "2")
    result = runner.invoke(meta_group, ["list", "--dir", str(snap_dir)])
    assert "alpha" in result.output
    assert "beta" in result.output
