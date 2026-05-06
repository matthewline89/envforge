"""Tests for envforge.cli_archive."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_archive import archive_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snaps"
    d.mkdir()
    (d / "dev.json").write_text(json.dumps({"ENV": "dev"}))
    (d / "prod.json").write_text(json.dumps({"ENV": "prod"}))
    return d


def test_create_cmd_reports_count(runner, snap_dir, tmp_path):
    out = str(tmp_path / "bundle.zip")
    result = runner.invoke(archive_group, ["create", out, "--snapshot-dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "2 snapshot(s)" in result.output


def test_create_cmd_lists_snapshot_names(runner, snap_dir, tmp_path):
    out = str(tmp_path / "bundle.zip")
    result = runner.invoke(archive_group, ["create", out, "--snapshot-dir", str(snap_dir)])
    assert "dev" in result.output
    assert "prod" in result.output


def test_create_cmd_filter_by_name(runner, snap_dir, tmp_path):
    out = str(tmp_path / "bundle.zip")
    result = runner.invoke(
        archive_group,
        ["create", out, "--snapshot-dir", str(snap_dir), "--name", "dev"],
    )
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" not in result.output


def test_create_cmd_error_on_missing_snapshot(runner, snap_dir, tmp_path):
    out = str(tmp_path / "bundle.zip")
    result = runner.invoke(
        archive_group,
        ["create", out, "--snapshot-dir", str(snap_dir), "--name", "ghost"],
    )
    assert result.exit_code == 1
    assert "Error" in result.output


def test_extract_cmd_restores_snapshots(runner, snap_dir, tmp_path):
    archive = str(tmp_path / "bundle.zip")
    runner.invoke(archive_group, ["create", archive, "--snapshot-dir", str(snap_dir)])

    dest = tmp_path / "restored"
    result = runner.invoke(archive_group, ["extract", archive, "--snapshot-dir", str(dest)])
    assert result.exit_code == 0
    assert "2 snapshot(s)" in result.output


def test_list_cmd_shows_snapshot_names(runner, snap_dir, tmp_path):
    archive = str(tmp_path / "bundle.zip")
    runner.invoke(archive_group, ["create", archive, "--snapshot-dir", str(snap_dir)])

    result = runner.invoke(archive_group, ["list", archive])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output


def test_list_cmd_error_on_missing_archive(runner, tmp_path):
    result = runner.invoke(archive_group, ["list", str(tmp_path / "ghost.zip")])
    assert result.exit_code != 0
