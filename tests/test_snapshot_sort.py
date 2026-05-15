"""Tests for envforge.snapshot_sort."""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from envforge.snapshot_sort import sort_snapshots, SortResult, SortedSnapshot


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(d: Path, name: str, env: dict) -> None:
    (d / f"{name}.json").write_text(json.dumps(env))


def test_sort_returns_sort_result(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "alpha", {"A": "1"})
    result = sort_snapshots(snapshot_dir)
    assert isinstance(result, SortResult)


def test_sort_items_are_sorted_snapshots(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "alpha", {"A": "1"})
    result = sort_snapshots(snapshot_dir)
    assert all(isinstance(i, SortedSnapshot) for i in result.items)


def test_sort_by_name_ascending(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "charlie", {})
    _write(snapshot_dir, "alpha", {})
    _write(snapshot_dir, "bravo", {})
    result = sort_snapshots(snapshot_dir, sort_key="name", ascending=True)
    names = [i.name for i in result.items]
    assert names == sorted(names)


def test_sort_by_name_descending(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "charlie", {})
    _write(snapshot_dir, "alpha", {})
    _write(snapshot_dir, "bravo", {})
    result = sort_snapshots(snapshot_dir, sort_key="name", ascending=False)
    names = [i.name for i in result.items]
    assert names == sorted(names, reverse=True)


def test_sort_by_keys(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "small", {"A": "1"})
    _write(snapshot_dir, "large", {"A": "1", "B": "2", "C": "3"})
    result = sort_snapshots(snapshot_dir, sort_key="keys", ascending=True)
    counts = [i.key_count for i in result.items]
    assert counts == sorted(counts)


def test_sort_by_size(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "tiny", {})
    _write(snapshot_dir, "big", {"LONG_KEY": "some_long_value_here"})
    result = sort_snapshots(snapshot_dir, sort_key="size", ascending=True)
    sizes = [i.size_bytes for i in result.items]
    assert sizes == sorted(sizes)


def test_sort_empty_dir_returns_empty_items(snapshot_dir: Path) -> None:
    result = sort_snapshots(snapshot_dir)
    assert result.items == []


def test_sort_result_stores_sort_key(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "x", {})
    result = sort_snapshots(snapshot_dir, sort_key="mtime")
    assert result.sort_key == "mtime"


def test_sort_result_stores_ascending_flag(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "x", {})
    result = sort_snapshots(snapshot_dir, ascending=False)
    assert result.ascending is False


def test_sorted_snapshot_has_mtime(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap", {"K": "V"})
    result = sort_snapshots(snapshot_dir)
    assert result.items[0].mtime > 0
