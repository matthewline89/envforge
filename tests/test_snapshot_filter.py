"""Tests for envforge.snapshot_filter."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_filter import (
    FilterResult,
    filter_by_key,
    filter_by_value,
    filter_by_predicate,
    filter_by_size,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _write(snapshot_dir: Path, name: str, env: dict[str, str]) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


def test_filter_result_is_empty_when_no_matches(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap1", {"FOO": "bar"})
    result = filter_by_key(snapshot_dir, "MISSING_*")
    assert result.is_empty()
    assert len(result) == 0


def test_filter_result_not_empty_with_match(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap1", {"FOO": "bar"})
    result = filter_by_key(snapshot_dir, "FOO")
    assert not result.is_empty()
    assert "snap1" in result.matched


def test_filter_by_key_glob_pattern(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap1", {"AWS_SECRET": "x", "HOME": "/home"})
    _write(snapshot_dir, "snap2", {"HOME": "/home"})
    result = filter_by_key(snapshot_dir, "AWS_*")
    assert "snap1" in result.matched
    assert "snap2" not in result.matched


def test_filter_by_key_case_insensitive(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap1", {"PATH": "/usr/bin"})
    result = filter_by_key(snapshot_dir, "path")
    assert "snap1" in result.matched


def test_filter_by_key_total_scanned(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap1", {"A": "1"})
    _write(snapshot_dir, "snap2", {"B": "2"})
    result = filter_by_key(snapshot_dir, "A")
    assert result.total_scanned == 2


def test_filter_by_value_finds_match(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap1", {"DB_URL": "postgres://localhost"})
    _write(snapshot_dir, "snap2", {"DB_URL": "mysql://localhost"})
    result = filter_by_value(snapshot_dir, "postgres*")
    assert "snap1" in result.matched
    assert "snap2" not in result.matched


def test_filter_by_value_no_match(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap1", {"KEY": "value"})
    result = filter_by_value(snapshot_dir, "NOPE")
    assert result.is_empty()


def test_filter_by_predicate_custom_logic(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap1", {"A": "1", "B": "2", "C": "3"})
    _write(snapshot_dir, "snap2", {"A": "1"})
    result = filter_by_predicate(snapshot_dir, lambda env: len(env) > 2)
    assert "snap1" in result.matched
    assert "snap2" not in result.matched


def test_filter_by_size_min_only(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap1", {"A": "1", "B": "2"})
    _write(snapshot_dir, "snap2", {"A": "1"})
    result = filter_by_size(snapshot_dir, min_keys=2)
    assert "snap1" in result.matched
    assert "snap2" not in result.matched


def test_filter_by_size_max_only(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap1", {"A": "1"})
    _write(snapshot_dir, "snap2", {"A": "1", "B": "2", "C": "3"})
    result = filter_by_size(snapshot_dir, max_keys=2)
    assert "snap1" in result.matched
    assert "snap2" not in result.matched


def test_filter_by_size_range(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap1", {"A": "1", "B": "2"})
    _write(snapshot_dir, "snap2", {"A": "1"})
    _write(snapshot_dir, "snap3", {"A": "1", "B": "2", "C": "3", "D": "4"})
    result = filter_by_size(snapshot_dir, min_keys=2, max_keys=3)
    assert "snap1" in result.matched
    assert "snap2" not in result.matched
    assert "snap3" not in result.matched


def test_filter_result_len(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap1", {"A": "1"})
    _write(snapshot_dir, "snap2", {"A": "1"})
    result = filter_by_key(snapshot_dir, "A")
    assert len(result) == 2
