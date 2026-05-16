"""Tests for envforge.snapshot_spotlight."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_spotlight import (
    SpotlightEntry,
    SpotlightReport,
    _compute_score,
    compute_spotlight,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envforge"
    d.mkdir()
    return d


def _write(directory: Path, name: str, env: dict) -> None:
    (directory / f"{name}.json").write_text(json.dumps(env))


# ---------------------------------------------------------------------------
# Unit tests for helpers
# ---------------------------------------------------------------------------

def test_compute_score_increases_with_rating() -> None:
    low = _compute_score(1, 0, 0)
    high = _compute_score(5, 0, 0)
    assert high > low


def test_compute_score_increases_with_access_count() -> None:
    low = _compute_score(0, 1, 0)
    high = _compute_score(0, 10, 0)
    assert high > low


def test_compute_score_caps_key_count_at_50() -> None:
    capped = _compute_score(0, 0, 50)
    over = _compute_score(0, 0, 100)
    assert capped == over


# ---------------------------------------------------------------------------
# SpotlightReport
# ---------------------------------------------------------------------------

def test_spotlight_report_is_empty_when_no_entries() -> None:
    report = SpotlightReport(entries=[])
    assert report.is_empty()


def test_spotlight_report_not_empty_with_entry() -> None:
    entry = SpotlightEntry(name="snap", score=5.0, rating=3, access_count=2, key_count=10)
    report = SpotlightReport(entries=[entry])
    assert not report.is_empty()


def test_spotlight_report_top_respects_n() -> None:
    entries = [
        SpotlightEntry(name=f"s{i}", score=float(i), rating=0, access_count=0, key_count=0)
        for i in range(10)
    ]
    report = SpotlightReport(entries=entries)
    assert len(report.top(3)) == 3


def test_spotlight_report_top_sorted_descending() -> None:
    entries = [
        SpotlightEntry(name="low", score=1.0, rating=0, access_count=0, key_count=0),
        SpotlightEntry(name="high", score=9.0, rating=0, access_count=0, key_count=0),
        SpotlightEntry(name="mid", score=5.0, rating=0, access_count=0, key_count=0),
    ]
    report = SpotlightReport(entries=entries)
    top = report.top(3)
    assert top[0].name == "high"
    assert top[-1].name == "low"


# ---------------------------------------------------------------------------
# compute_spotlight integration
# ---------------------------------------------------------------------------

def test_compute_spotlight_returns_spotlight_report(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "alpha", {"K": "v"})
    result = compute_spotlight(snapshot_dir)
    assert isinstance(result, SpotlightReport)


def test_compute_spotlight_includes_all_snapshots(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "a", {"X": "1"})
    _write(snapshot_dir, "b", {"Y": "2"})
    result = compute_spotlight(snapshot_dir)
    names = {e.name for e in result.entries}
    assert "a" in names
    assert "b" in names


def test_compute_spotlight_empty_dir_gives_empty_report(snapshot_dir: Path) -> None:
    result = compute_spotlight(snapshot_dir)
    assert result.is_empty()
