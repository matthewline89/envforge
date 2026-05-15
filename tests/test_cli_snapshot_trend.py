"""Tests for envforge.cli_snapshot_trend."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envforge.cli_snapshot_trend import trend_group
from envforge.snapshot_trend import TrendPoint, TrendReport


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envforge"
    d.mkdir()
    return d


def _write(snap_dir: Path, name: str, env: dict) -> None:
    (snap_dir / f"{name}.json").write_text(json.dumps(env))


def _fake_trend(report: TrendReport):
    return patch("envforge.cli_snapshot_trend.build_trend", return_value=report)


def test_show_cmd_no_data_message(runner, snap_dir):
    empty_report = TrendReport(name="snap")
    with _fake_trend(empty_report):
        result = runner.invoke(
            trend_group, ["show", "snap", "--dir", str(snap_dir)]
        )
    assert result.exit_code == 0
    assert "No trend data" in result.output


def test_show_cmd_prints_trend_header(runner, snap_dir):
    pts = [TrendPoint("2024-01-01T00:00:00", 3, "init"), TrendPoint("2024-06-01T00:00:00", 5, "current")]
    report = TrendReport(name="snap", points=pts)
    with _fake_trend(report):
        result = runner.invoke(
            trend_group, ["show", "snap", "--dir", str(snap_dir)]
        )
    assert result.exit_code == 0
    assert "Trend for 'snap'" in result.output


def test_show_cmd_prints_min_max(runner, snap_dir):
    pts = [TrendPoint("2024-01-01T00:00:00", 2), TrendPoint("2024-06-01T00:00:00", 8)]
    report = TrendReport(name="snap", points=pts)
    with _fake_trend(report):
        result = runner.invoke(
            trend_group, ["show", "snap", "--dir", str(snap_dir)]
        )
    assert "min keys" in result.output
    assert "max keys" in result.output


def test_show_cmd_prints_positive_delta(runner, snap_dir):
    pts = [TrendPoint("t1", 2), TrendPoint("t2", 5)]
    report = TrendReport(name="snap", points=pts)
    with _fake_trend(report):
        result = runner.invoke(
            trend_group, ["show", "snap", "--dir", str(snap_dir)]
        )
    assert "+3" in result.output


def test_show_cmd_prints_each_point(runner, snap_dir):
    pts = [
        TrendPoint("2024-01-01T00:00:00", 3, "init"),
        TrendPoint("2024-06-01T00:00:00", 6, "current"),
    ]
    report = TrendReport(name="snap", points=pts)
    with _fake_trend(report):
        result = runner.invoke(
            trend_group, ["show", "snap", "--dir", str(snap_dir)]
        )
    assert "keys=3" in result.output
    assert "keys=6" in result.output
