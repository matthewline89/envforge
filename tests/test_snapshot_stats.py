"""Tests for envforge.snapshot_stats."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_stats import SnapshotStats, compute_stats, summary


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


# ---------------------------------------------------------------------------
# compute_stats
# ---------------------------------------------------------------------------

def test_compute_stats_returns_snapshot_stats(snapshot_dir):
    _write(snapshot_dir, "dev", {"HOME": "/home/user", "PATH": "/usr/bin"})
    result = compute_stats(snapshot_dir, "dev")
    assert isinstance(result, SnapshotStats)


def test_compute_stats_total_keys(snapshot_dir):
    _write(snapshot_dir, "dev", {"A": "1", "B": "2", "C": "3"})
    stats = compute_stats(snapshot_dir, "dev")
    assert stats.total_keys == 3


def test_compute_stats_empty_values(snapshot_dir):
    _write(snapshot_dir, "dev", {"PRESENT": "yes", "EMPTY": ""})
    stats = compute_stats(snapshot_dir, "dev")
    assert "EMPTY" in stats.empty_values
    assert "PRESENT" not in stats.empty_values


def test_compute_stats_empty_count(snapshot_dir):
    _write(snapshot_dir, "dev", {"X": "", "Y": "", "Z": "val"})
    stats = compute_stats(snapshot_dir, "dev")
    assert stats.empty_count == 2


def test_compute_stats_longest_key(snapshot_dir):
    _write(snapshot_dir, "dev", {"SHORT": "a", "VERY_LONG_KEY_NAME": "b"})
    stats = compute_stats(snapshot_dir, "dev")
    assert stats.longest_key == "VERY_LONG_KEY_NAME"


def test_compute_stats_longest_value_key(snapshot_dir):
    _write(snapshot_dir, "dev", {"K1": "short", "K2": "a" * 50})
    stats = compute_stats(snapshot_dir, "dev")
    assert stats.longest_value_key == "K2"


def test_compute_stats_avg_key_length(snapshot_dir):
    # keys: "AB" (2), "ABCD" (4) -> avg 3.0
    _write(snapshot_dir, "dev", {"AB": "x", "ABCD": "y"})
    stats = compute_stats(snapshot_dir, "dev")
    assert stats.avg_key_length == pytest.approx(3.0)


def test_compute_stats_empty_snapshot(snapshot_dir):
    _write(snapshot_dir, "empty", {})
    stats = compute_stats(snapshot_dir, "empty")
    assert stats.total_keys == 0
    assert stats.avg_key_length == 0.0
    assert stats.avg_value_length == 0.0
    assert stats.longest_key == ""


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------

def test_summary_contains_snapshot_name(snapshot_dir):
    _write(snapshot_dir, "prod", {"KEY": "val"})
    stats = compute_stats(snapshot_dir, "prod")
    assert "prod" in summary(stats)


def test_summary_contains_total_keys(snapshot_dir):
    _write(snapshot_dir, "prod", {"A": "1", "B": "2"})
    stats = compute_stats(snapshot_dir, "prod")
    assert "2" in summary(stats)


def test_summary_contains_empty_count(snapshot_dir):
    _write(snapshot_dir, "prod", {"A": ""})
    stats = compute_stats(snapshot_dir, "prod")
    result = summary(stats)
    assert "Empty values" in result
