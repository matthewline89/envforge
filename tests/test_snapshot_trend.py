"""Tests for envforge.snapshot_trend."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from envforge.snapshot_trend import TrendPoint, TrendReport, build_trend


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envforge"
    d.mkdir()
    return d


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


def _fake_history(entries):
    return patch("envforge.snapshot_trend.get_history", return_value=entries)


# ---------------------------------------------------------------------------
# TrendReport helpers
# ---------------------------------------------------------------------------

def test_trend_report_is_empty_when_no_points():
    report = TrendReport(name="x")
    assert report.is_empty


def test_trend_report_not_empty_with_points():
    report = TrendReport(name="x", points=[TrendPoint("2024-01-01", 3)])
    assert not report.is_empty


def test_trend_report_min_max():
    pts = [TrendPoint("t1", 2), TrendPoint("t2", 5), TrendPoint("t3", 1)]
    report = TrendReport(name="x", points=pts)
    assert report.min_keys == 1
    assert report.max_keys == 5


def test_trend_report_delta():
    pts = [TrendPoint("t1", 3), TrendPoint("t2", 7)]
    report = TrendReport(name="x", points=pts)
    assert report.delta == 4


def test_trend_report_delta_negative():
    pts = [TrendPoint("t1", 10), TrendPoint("t2", 4)]
    report = TrendReport(name="x", points=pts)
    assert report.delta == -6


def test_trend_report_delta_single_point():
    report = TrendReport(name="x", points=[TrendPoint("t1", 5)])
    assert report.delta == 0


# ---------------------------------------------------------------------------
# build_trend
# ---------------------------------------------------------------------------

def test_build_trend_returns_trend_report(snapshot_dir):
    _write(snapshot_dir, "snap", {"A": "1"})
    with _fake_history([]):
        result = build_trend("snap", snapshot_dir)
    assert isinstance(result, TrendReport)
    assert result.name == "snap"


def test_build_trend_includes_history_points(snapshot_dir):
    _write(snapshot_dir, "snap", {"A": "1"})
    history = [
        {"timestamp": "2024-01-01T00:00:00", "vars": {"A": "1", "B": "2"}, "note": "init"},
    ]
    with _fake_history(history):
        result = build_trend("snap", snapshot_dir)
    # one history point + one current point
    assert len(result.points) >= 2


def test_build_trend_skips_entries_without_vars(snapshot_dir):
    _write(snapshot_dir, "snap", {"A": "1"})
    history = [
        {"timestamp": "2024-01-01T00:00:00"},  # no 'vars' key
    ]
    with _fake_history(history):
        result = build_trend("snap", snapshot_dir)
    # only the current-state point should be present
    assert len(result.points) == 1
    assert result.points[0].note == "current"


def test_build_trend_current_point_key_count(snapshot_dir):
    _write(snapshot_dir, "snap", {"A": "1", "B": "2", "C": "3"})
    with _fake_history([]):
        result = build_trend("snap", snapshot_dir)
    assert result.points[-1].key_count == 3


def test_build_trend_missing_snapshot_no_current_point(snapshot_dir):
    with _fake_history([]):
        result = build_trend("nonexistent", snapshot_dir)
    assert result.is_empty
