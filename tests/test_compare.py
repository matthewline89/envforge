"""Tests for envforge.compare module."""

from __future__ import annotations

import json
import pathlib

import pytest

from envforge.compare import (
    CompareReport,
    build_matrix,
    compare_snapshots,
)


@pytest.fixture()
def snapshot_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path


def _write(directory: pathlib.Path, name: str, data: dict) -> None:
    (directory / f"{name}.json").write_text(json.dumps(data))


def test_compare_requires_at_least_two_snapshots(snapshot_dir):
    _write(snapshot_dir, "a", {"X": "1"})
    with pytest.raises(ValueError, match="At least two"):
        compare_snapshots(["a"], snapshot_dir=snapshot_dir)


def test_compare_returns_report(snapshot_dir):
    _write(snapshot_dir, "a", {"X": "1"})
    _write(snapshot_dir, "b", {"X": "1"})
    report = compare_snapshots(["a", "b"], snapshot_dir=snapshot_dir)
    assert isinstance(report, CompareReport)


def test_matrix_contains_all_keys(snapshot_dir):
    _write(snapshot_dir, "a", {"X": "1", "Y": "2"})
    _write(snapshot_dir, "b", {"Y": "2", "Z": "3"})
    matrix = build_matrix(["a", "b"], snapshot_dir=snapshot_dir)
    assert set(matrix.keys()) == {"X", "Y", "Z"}


def test_common_keys_only_shared(snapshot_dir):
    _write(snapshot_dir, "a", {"X": "1", "SHARED": "v"})
    _write(snapshot_dir, "b", {"SHARED": "v", "Z": "3"})
    report = compare_snapshots(["a", "b"], snapshot_dir=snapshot_dir)
    assert report.common_keys() == {"SHARED"}


def test_unique_keys_per_snapshot(snapshot_dir):
    _write(snapshot_dir, "a", {"ONLY_A": "1", "SHARED": "v"})
    _write(snapshot_dir, "b", {"ONLY_B": "2", "SHARED": "v"})
    report = compare_snapshots(["a", "b"], snapshot_dir=snapshot_dir)
    unique = report.unique_keys()
    assert unique["a"] == {"ONLY_A"}
    assert unique["b"] == {"ONLY_B"}


def test_differing_keys_detects_value_change(snapshot_dir):
    _write(snapshot_dir, "a", {"K": "old", "SAME": "x"})
    _write(snapshot_dir, "b", {"K": "new", "SAME": "x"})
    report = compare_snapshots(["a", "b"], snapshot_dir=snapshot_dir)
    assert "K" in report.differing_keys()
    assert "SAME" not in report.differing_keys()


def test_differing_keys_empty_when_identical(snapshot_dir):
    data = {"A": "1", "B": "2"}
    _write(snapshot_dir, "a", data)
    _write(snapshot_dir, "b", data)
    report = compare_snapshots(["a", "b"], snapshot_dir=snapshot_dir)
    assert len(report.differing_keys()) == 0


def test_three_snapshot_comparison(snapshot_dir):
    _write(snapshot_dir, "a", {"X": "1"})
    _write(snapshot_dir, "b", {"X": "2"})
    _write(snapshot_dir, "c", {"X": "1"})
    report = compare_snapshots(["a", "b", "c"], snapshot_dir=snapshot_dir)
    assert "X" in report.differing_keys()
    assert report.snapshot_names == ["a", "b", "c"]


def test_missing_value_shows_none_in_matrix(snapshot_dir):
    _write(snapshot_dir, "a", {"PRESENT": "yes"})
    _write(snapshot_dir, "b", {})
    report = compare_snapshots(["a", "b"], snapshot_dir=snapshot_dir)
    assert report.matrix["PRESENT"]["b"] is None
