"""Tests for envforge.snapshot_digest."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_digest import (
    DigestInfo,
    _compute_digest,
    digest_snapshot,
    digests_match,
    find_duplicates,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


# --- _compute_digest ---

def test_compute_digest_returns_string() -> None:
    result = _compute_digest({"A": "1"})
    assert isinstance(result, str)
    assert len(result) == 64  # SHA-256 hex


def test_compute_digest_is_stable() -> None:
    assert _compute_digest({"A": "1", "B": "2"}) == _compute_digest({"B": "2", "A": "1"})


def test_compute_digest_differs_for_different_envs() -> None:
    assert _compute_digest({"A": "1"}) != _compute_digest({"A": "2"})


# --- digest_snapshot ---

def test_digest_snapshot_returns_digest_info(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap1", {"X": "y"})
    info = digest_snapshot(snapshot_dir, "snap1")
    assert isinstance(info, DigestInfo)


def test_digest_snapshot_name_matches(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap1", {"X": "y"})
    info = digest_snapshot(snapshot_dir, "snap1")
    assert info.name == "snap1"


def test_digest_snapshot_key_count(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap1", {"A": "1", "B": "2", "C": "3"})
    info = digest_snapshot(snapshot_dir, "snap1")
    assert info.key_count == 3


def test_digest_snapshot_raises_for_missing(snapshot_dir: Path) -> None:
    with pytest.raises(FileNotFoundError):
        digest_snapshot(snapshot_dir, "ghost")


# --- digests_match ---

def test_digests_match_returns_true_for_identical(snapshot_dir: Path) -> None:
    env = {"KEY": "value"}
    _write(snapshot_dir, "a", env)
    _write(snapshot_dir, "b", env)
    assert digests_match(snapshot_dir, "a", "b") is True


def test_digests_match_returns_false_for_different(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "a", {"KEY": "value"})
    _write(snapshot_dir, "b", {"KEY": "other"})
    assert digests_match(snapshot_dir, "a", "b") is False


# --- find_duplicates ---

def test_find_duplicates_returns_empty_when_no_dupes(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "a", {"A": "1"})
    _write(snapshot_dir, "b", {"B": "2"})
    assert find_duplicates(snapshot_dir) == {}


def test_find_duplicates_groups_identical_snapshots(snapshot_dir: Path) -> None:
    env = {"SAME": "value"}
    _write(snapshot_dir, "x", env)
    _write(snapshot_dir, "y", env)
    _write(snapshot_dir, "z", {"OTHER": "val"})
    groups = find_duplicates(snapshot_dir)
    assert len(groups) == 1
    names = next(iter(groups.values()))
    assert sorted(names) == ["x", "y"]


def test_find_duplicates_accepts_explicit_names(snapshot_dir: Path) -> None:
    env = {"K": "v"}
    _write(snapshot_dir, "p", env)
    _write(snapshot_dir, "q", env)
    _write(snapshot_dir, "r", env)
    groups = find_duplicates(snapshot_dir, names=["p", "q"])
    assert len(groups) == 1
    names = next(iter(groups.values()))
    assert sorted(names) == ["p", "q"]
