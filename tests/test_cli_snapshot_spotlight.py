"""Tests for envforge.cli_snapshot_spotlight."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envforge.cli_snapshot_spotlight import spotlight_group
from envforge.snapshot_spotlight import SpotlightEntry, SpotlightReport


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envforge"
    d.mkdir()
    return d


def _write(directory: Path, name: str, env: dict) -> None:
    (directory / f"{name}.json").write_text(json.dumps(env))


def _fake_report(entries):
    return SpotlightReport(entries=entries)


def test_show_cmd_no_snapshots_message(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(spotlight_group, ["show", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No snapshots found" in result.output


def test_show_cmd_prints_header(runner: CliRunner, snap_dir: Path) -> None:
    _write(snap_dir, "mysnap", {"A": "1"})
    result = runner.invoke(spotlight_group, ["show", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "Name" in result.output
    assert "Score" in result.output


def test_show_cmd_prints_snapshot_name(runner: CliRunner, snap_dir: Path) -> None:
    _write(snap_dir, "featured", {"FOO": "bar"})
    result = runner.invoke(spotlight_group, ["show", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "featured" in result.output


def test_show_cmd_top_option_limits_output(runner: CliRunner, snap_dir: Path) -> None:
    entries = [
        SpotlightEntry(name=f"snap{i}", score=float(i), rating=0, access_count=0, key_count=0)
        for i in range(10)
    ]
    report = SpotlightReport(entries=entries)
    with patch("envforge.cli_snapshot_spotlight.compute_spotlight", return_value=report):
        result = runner.invoke(spotlight_group, ["show", "--dir", str(snap_dir), "--top", "3"])
    assert result.exit_code == 0
    # 3 data rows + header + separator
    lines = [l for l in result.output.splitlines() if l.strip()]
    assert len(lines) == 5


def test_top_cmd_prints_names_only(runner: CliRunner, snap_dir: Path) -> None:
    entries = [
        SpotlightEntry(name="best", score=10.0, rating=5, access_count=3, key_count=20),
        SpotlightEntry(name="second", score=5.0, rating=3, access_count=1, key_count=10),
    ]
    report = SpotlightReport(entries=entries)
    with patch("envforge.cli_snapshot_spotlight.compute_spotlight", return_value=report):
        result = runner.invoke(spotlight_group, ["top", "2", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "best" in result.output
    assert "second" in result.output


def test_top_cmd_no_snapshots_message(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(spotlight_group, ["top", "3", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No snapshots found" in result.output
