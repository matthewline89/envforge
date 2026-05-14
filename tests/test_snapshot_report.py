"""Tests for envforge.snapshot_report."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from envforge.snapshot_report import (
    SnapshotReport,
    SnapshotReportEntry,
    build_report,
    format_report,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    p = snapshot_dir / f"{name}.json"
    p.write_text(json.dumps(env))


# ---------------------------------------------------------------------------
# SnapshotReport helpers
# ---------------------------------------------------------------------------

def test_report_total_snapshots():
    entry = SnapshotReportEntry(
        name="a", total_keys=3, empty_values=0,
        lint_errors=0, lint_warnings=0, expires_at=None, is_expired=False,
    )
    report = SnapshotReport(entries=[entry])
    assert report.total_snapshots == 1


def test_report_snapshots_with_errors():
    ok = SnapshotReportEntry(
        name="ok", total_keys=2, empty_values=0,
        lint_errors=0, lint_warnings=0, expires_at=None, is_expired=False,
    )
    bad = SnapshotReportEntry(
        name="bad", total_keys=1, empty_values=1,
        lint_errors=2, lint_warnings=0, expires_at=None, is_expired=False,
    )
    report = SnapshotReport(entries=[ok, bad])
    assert report.snapshots_with_errors == 1


def test_report_expired_count():
    e1 = SnapshotReportEntry(
        name="x", total_keys=1, empty_values=0,
        lint_errors=0, lint_warnings=0, expires_at="2000-01-01", is_expired=True,
    )
    e2 = SnapshotReportEntry(
        name="y", total_keys=1, empty_values=0,
        lint_errors=0, lint_warnings=0, expires_at=None, is_expired=False,
    )
    report = SnapshotReport(entries=[e1, e2])
    assert report.expired_count == 1


# ---------------------------------------------------------------------------
# build_report
# ---------------------------------------------------------------------------

def test_build_report_returns_snapshot_report(snapshot_dir):
    _write(snapshot_dir, "env1", {"KEY": "val"})
    report = build_report(snapshot_dir)
    assert isinstance(report, SnapshotReport)


def test_build_report_includes_all_snapshots(snapshot_dir):
    _write(snapshot_dir, "alpha", {"A": "1"})
    _write(snapshot_dir, "beta", {"B": "2"})
    report = build_report(snapshot_dir)
    names = {e.name for e in report.entries}
    assert "alpha" in names
    assert "beta" in names


def test_build_report_filters_by_name(snapshot_dir):
    _write(snapshot_dir, "alpha", {"A": "1"})
    _write(snapshot_dir, "beta", {"B": "2"})
    report = build_report(snapshot_dir, names=["alpha"])
    assert report.total_snapshots == 1
    assert report.entries[0].name == "alpha"


def test_build_report_skips_missing_names(snapshot_dir):
    report = build_report(snapshot_dir, names=["ghost"])
    assert report.total_snapshots == 0


def test_build_report_records_total_keys(snapshot_dir):
    _write(snapshot_dir, "env1", {"A": "1", "B": "2", "C": "3"})
    report = build_report(snapshot_dir, names=["env1"])
    assert report.entries[0].total_keys == 3


# ---------------------------------------------------------------------------
# format_report
# ---------------------------------------------------------------------------

def test_format_report_contains_snapshot_name(snapshot_dir):
    _write(snapshot_dir, "mysnap", {"X": "y"})
    report = build_report(snapshot_dir, names=["mysnap"])
    text = format_report(report)
    assert "mysnap" in text


def test_format_report_shows_totals_line(snapshot_dir):
    _write(snapshot_dir, "s1", {"K": "v"})
    report = build_report(snapshot_dir, names=["s1"])
    text = format_report(report)
    assert "Total:" in text


def test_format_report_ok_status_for_clean_snapshot(snapshot_dir):
    _write(snapshot_dir, "clean", {"VALID_KEY": "value"})
    report = build_report(snapshot_dir, names=["clean"])
    text = format_report(report)
    assert "OK" in text
