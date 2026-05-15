"""Tests for envforge.snapshot_count."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_count import (
    CountEntry,
    CountReport,
    count_snapshot,
    count_all,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


def test_count_snapshot_returns_count_entry(snapshot_dir):
    _write(snapshot_dir, "s1", {"A": "1", "B": "2"})
    entry = count_snapshot("s1", snapshot_dir)
    assert isinstance(entry, CountEntry)


def test_count_snapshot_name_matches(snapshot_dir):
    _write(snapshot_dir, "s1", {"A": "1"})
    entry = count_snapshot("s1", snapshot_dir)
    assert entry.name == "s1"


def test_count_snapshot_total_keys(snapshot_dir):
    _write(snapshot_dir, "s1", {"A": "1", "B": "2", "C": "3"})
    entry = count_snapshot("s1", snapshot_dir)
    assert entry.total == 3


def test_count_snapshot_empty_values(snapshot_dir):
    _write(snapshot_dir, "s1", {"A": "", "B": "hello", "C": ""})
    entry = count_snapshot("s1", snapshot_dir)
    assert entry.empty == 2
    assert entry.non_empty == 1


def test_count_snapshot_no_empty_values(snapshot_dir):
    _write(snapshot_dir, "s1", {"A": "x", "B": "y"})
    entry = count_snapshot("s1", snapshot_dir)
    assert entry.empty == 0
    assert entry.non_empty == 2


def test_count_all_returns_count_report(snapshot_dir):
    _write(snapshot_dir, "s1", {"A": "1"})
    report = count_all(snapshot_dir)
    assert isinstance(report, CountReport)


def test_count_all_total_snapshots(snapshot_dir):
    _write(snapshot_dir, "s1", {"A": "1"})
    _write(snapshot_dir, "s2", {"B": "2"})
    report = count_all(snapshot_dir)
    assert report.total_snapshots == 2


def test_count_all_grand_total_keys(snapshot_dir):
    _write(snapshot_dir, "s1", {"A": "1", "B": "2"})
    _write(snapshot_dir, "s2", {"C": "3"})
    report = count_all(snapshot_dir)
    assert report.grand_total_keys == 3


def test_count_all_grand_total_empty(snapshot_dir):
    _write(snapshot_dir, "s1", {"A": "", "B": "x"})
    _write(snapshot_dir, "s2", {"C": ""})
    report = count_all(snapshot_dir)
    assert report.grand_total_empty == 2


def test_count_all_min_keys_filter(snapshot_dir):
    _write(snapshot_dir, "small", {"A": "1"})
    _write(snapshot_dir, "large", {"A": "1", "B": "2", "C": "3"})
    report = count_all(snapshot_dir, min_keys=2)
    assert report.total_snapshots == 1
    assert report.entries[0].name == "large"


def test_count_all_max_keys_filter(snapshot_dir):
    _write(snapshot_dir, "small", {"A": "1"})
    _write(snapshot_dir, "large", {"A": "1", "B": "2", "C": "3"})
    report = count_all(snapshot_dir, max_keys=2)
    assert report.total_snapshots == 1
    assert report.entries[0].name == "small"


def test_count_all_empty_dir(snapshot_dir):
    report = count_all(snapshot_dir)
    assert report.total_snapshots == 0
    assert report.grand_total_keys == 0
