"""Tests for envforge.snapshot_popularity."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_popularity import (
    PopularityEntry,
    PopularityReport,
    _compute_score,
    compute_popularity,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write_access(snapshot_dir: Path, data: dict) -> None:
    path = snapshot_dir / "access.json"
    path.write_text(json.dumps(data))


def _write_activity(snapshot_dir: Path, data: dict) -> None:
    path = snapshot_dir / "activity.json"
    path.write_text(json.dumps(data))


# --- unit tests for helpers ---

def test_compute_score_weights_access_higher():
    assert _compute_score(3, 1) > _compute_score(1, 3)


def test_compute_score_zero_inputs():
    assert _compute_score(0, 0) == 0.0


def test_compute_score_formula():
    assert _compute_score(2, 4) == pytest.approx(8.0)


# --- PopularityReport ---

def test_report_is_empty_when_no_entries():
    report = PopularityReport(entries=[])
    assert report.is_empty()


def test_report_not_empty_with_entry():
    entry = PopularityEntry(name="snap", access_count=1, activity_count=0, score=2.0)
    report = PopularityReport(entries=[entry])
    assert not report.is_empty()


def test_top_returns_n_entries():
    entries = [
        PopularityEntry(name=f"snap{i}", access_count=i, activity_count=0, score=float(i))
        for i in range(10)
    ]
    report = PopularityReport(entries=entries)
    assert len(report.top(3)) == 3


def test_top_sorted_by_score_descending():
    entries = [
        PopularityEntry(name="a", access_count=1, activity_count=0, score=2.0),
        PopularityEntry(name="b", access_count=5, activity_count=0, score=10.0),
        PopularityEntry(name="c", access_count=3, activity_count=0, score=6.0),
    ]
    report = PopularityReport(entries=entries)
    top = report.top(3)
    assert [e.name for e in top] == ["b", "c", "a"]


def test_rank_of_returns_correct_position():
    entries = [
        PopularityEntry(name="a", access_count=1, activity_count=0, score=2.0),
        PopularityEntry(name="b", access_count=5, activity_count=0, score=10.0),
    ]
    report = PopularityReport(entries=entries)
    assert report.rank_of("b") == 1
    assert report.rank_of("a") == 2


def test_rank_of_returns_none_for_unknown():
    report = PopularityReport(entries=[])
    assert report.rank_of("missing") is None


# --- compute_popularity integration ---

def test_compute_popularity_returns_report(snapshot_dir):
    _write_access(snapshot_dir, {"snap1": {"count": 3}})
    _write_activity(snapshot_dir, {"snap1": [{"action": "save"}]})
    report = compute_popularity(snapshot_dir)
    assert isinstance(report, PopularityReport)


def test_compute_popularity_combines_sources(snapshot_dir):
    _write_access(snapshot_dir, {"snap1": {"count": 4}})
    _write_activity(snapshot_dir, {"snap2": [{"action": "save"}, {"action": "load"}]})
    report = compute_popularity(snapshot_dir)
    names = {e.name for e in report.entries}
    assert "snap1" in names
    assert "snap2" in names


def test_compute_popularity_score_reflects_access(snapshot_dir):
    _write_access(snapshot_dir, {"snap1": {"count": 5}})
    _write_activity(snapshot_dir, {})
    report = compute_popularity(snapshot_dir)
    entry = report.entries[0]
    assert entry.score == pytest.approx(10.0)


def test_compute_popularity_empty_dir_returns_empty_report(snapshot_dir):
    report = compute_popularity(snapshot_dir)
    assert report.is_empty()
