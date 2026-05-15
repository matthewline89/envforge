"""Tests for envforge.cli_snapshot_health."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envforge.cli_snapshot_health import health_group
from envforge.snapshot_health import HealthReport
from envforge.lint import LintReport


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(snap_dir: Path, name: str, env: dict) -> None:
    (snap_dir / f"{name}.json").write_text(json.dumps(env))


def _ok_report(name: str) -> HealthReport:
    return HealthReport(
        name=name,
        lint=LintReport(issues=[]),
        expired=False,
        locked=False,
        frozen=False,
    )


def test_show_cmd_prints_status(runner, snap_dir):
    _write(snap_dir, "mysnap", {"K": "v"})
    with patch("envforge.cli_snapshot_health.check_health", return_value=_ok_report("mysnap")):
        result = runner.invoke(health_group, ["show", "mysnap", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "mysnap" in result.output
    assert "ok" in result.output.lower()


def test_show_cmd_prints_locked_and_frozen(runner, snap_dir):
    _write(snap_dir, "s", {"K": "v"})
    report = _ok_report("s")
    report.locked = True
    report.frozen = True
    with patch("envforge.cli_snapshot_health.check_health", return_value=report):
        result = runner.invoke(health_group, ["show", "s", "--dir", str(snap_dir)])
    assert "yes" in result.output


def test_scan_cmd_no_snapshots(runner, snap_dir):
    result = runner.invoke(health_group, ["scan", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No snapshots" in result.output


def test_scan_cmd_lists_snapshots(runner, snap_dir):
    _write(snap_dir, "alpha", {"A": "1"})
    _write(snap_dir, "beta", {"B": "2"})
    with patch("envforge.cli_snapshot_health.check_health", side_effect=lambda n, _: _ok_report(n)):
        result = runner.invoke(health_group, ["scan", "--dir", str(snap_dir)])
    assert "alpha" in result.output
    assert "beta" in result.output


def test_scan_cmd_errors_only_hides_healthy(runner, snap_dir):
    _write(snap_dir, "good", {"A": "1"})
    with patch("envforge.cli_snapshot_health.check_health", return_value=_ok_report("good")):
        result = runner.invoke(health_group, ["scan", "--errors-only", "--dir", str(snap_dir)])
    assert "good" not in result.output
