"""Tests for envforge.snapshot_size."""
from pathlib import Path
import json
import pytest

from envforge.snapshot_size import (
    SizeInfo,
    SizeReport,
    size_snapshot,
    size_report,
    largest_snapshot,
    smallest_snapshot,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    path = snapshot_dir / f"{name}.json"
    path.write_text(json.dumps(env))


def test_size_snapshot_returns_size_info(snapshot_dir):
    _write(snapshot_dir, "alpha", {"FOO": "bar"})
    result = size_snapshot("alpha", snapshot_dir)
    assert isinstance(result, SizeInfo)


def test_size_snapshot_name_matches(snapshot_dir):
    _write(snapshot_dir, "alpha", {"FOO": "bar"})
    result = size_snapshot("alpha", snapshot_dir)
    assert result.name == "alpha"


def test_size_snapshot_key_count(snapshot_dir):
    _write(snapshot_dir, "alpha", {"A": "1", "B": "2", "C": "3"})
    result = size_snapshot("alpha", snapshot_dir)
    assert result.key_count == 3


def test_size_snapshot_total_chars(snapshot_dir):
    _write(snapshot_dir, "alpha", {"KEY": "VAL"})
    result = size_snapshot("alpha", snapshot_dir)
    # "KEY" (3) + "VAL" (3) = 6
    assert result.total_chars == 6


def test_size_snapshot_largest_key(snapshot_dir):
    _write(snapshot_dir, "alpha", {"SHORT": "x", "MUCH_LONGER_KEY": "x"})
    result = size_snapshot("alpha", snapshot_dir)
    assert result.largest_key == "MUCH_LONGER_KEY"


def test_size_snapshot_largest_value_key(snapshot_dir):
    _write(snapshot_dir, "alpha", {"A": "short", "B": "a_very_long_value_here"})
    result = size_snapshot("alpha", snapshot_dir)
    assert result.largest_value_key == "B"


def test_size_snapshot_empty_env(snapshot_dir):
    _write(snapshot_dir, "empty", {})
    result = size_snapshot("empty", snapshot_dir)
    assert result.key_count == 0
    assert result.total_chars == 0
    assert result.largest_key == ""
    assert result.largest_value_key == ""


def test_size_report_returns_size_report(snapshot_dir):
    _write(snapshot_dir, "s1", {"X": "1"})
    report = size_report(snapshot_dir)
    assert isinstance(report, SizeReport)


def test_size_report_includes_all_snapshots(snapshot_dir):
    _write(snapshot_dir, "s1", {"X": "1"})
    _write(snapshot_dir, "s2", {"Y": "2"})
    report = size_report(snapshot_dir)
    names = {e.name for e in report.entries}
    assert names == {"s1", "s2"}


def test_largest_snapshot_returns_biggest(snapshot_dir):
    _write(snapshot_dir, "small", {"A": "1"})
    _write(snapshot_dir, "big", {"LONGKEY": "LONGVALUE_EXTRA"})
    report = size_report(snapshot_dir)
    result = largest_snapshot(report)
    assert result is not None
    assert result.name == "big"


def test_smallest_snapshot_returns_smallest(snapshot_dir):
    _write(snapshot_dir, "small", {"A": "1"})
    _write(snapshot_dir, "big", {"LONGKEY": "LONGVALUE_EXTRA"})
    report = size_report(snapshot_dir)
    result = smallest_snapshot(report)
    assert result is not None
    assert result.name == "small"


def test_largest_snapshot_none_when_empty():
    report = SizeReport(entries=[])
    assert largest_snapshot(report) is None


def test_smallest_snapshot_none_when_empty():
    report = SizeReport(entries=[])
    assert smallest_snapshot(report) is None
