"""Tests for envforge.snapshot_quota."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_quota import (
    QuotaResult,
    check_quota,
    get_quota,
    remove_quota,
    set_quota,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snaps"


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


# --- set_quota ---

def test_set_quota_creates_quota_file(snapshot_dir: Path) -> None:
    set_quota(snapshot_dir, 5)
    assert (snapshot_dir / ".quota.json").exists()


def test_set_quota_stores_limit(snapshot_dir: Path) -> None:
    set_quota(snapshot_dir, 10)
    assert get_quota(snapshot_dir) == 10


def test_set_quota_overwrites_existing(snapshot_dir: Path) -> None:
    set_quota(snapshot_dir, 3)
    set_quota(snapshot_dir, 7)
    assert get_quota(snapshot_dir) == 7


def test_set_quota_raises_for_zero(snapshot_dir: Path) -> None:
    with pytest.raises(ValueError):
        set_quota(snapshot_dir, 0)


def test_set_quota_raises_for_negative(snapshot_dir: Path) -> None:
    with pytest.raises(ValueError):
        set_quota(snapshot_dir, -1)


# --- get_quota ---

def test_get_quota_returns_none_when_not_set(snapshot_dir: Path) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    assert get_quota(snapshot_dir) is None


# --- remove_quota ---

def test_remove_quota_returns_true_when_found(snapshot_dir: Path) -> None:
    set_quota(snapshot_dir, 5)
    assert remove_quota(snapshot_dir) is True


def test_remove_quota_returns_false_when_missing(snapshot_dir: Path) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    assert remove_quota(snapshot_dir) is False


def test_remove_quota_clears_limit(snapshot_dir: Path) -> None:
    set_quota(snapshot_dir, 5)
    remove_quota(snapshot_dir)
    assert get_quota(snapshot_dir) is None


# --- check_quota ---

def test_check_quota_raises_when_no_quota(snapshot_dir: Path) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    with pytest.raises(ValueError):
        check_quota(snapshot_dir)


def test_check_quota_returns_quota_result(snapshot_dir: Path) -> None:
    set_quota(snapshot_dir, 5)
    result = check_quota(snapshot_dir)
    assert isinstance(result, QuotaResult)


def test_check_quota_not_exceeded_when_under_limit(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "a", {"X": "1"})
    set_quota(snapshot_dir, 3)
    result = check_quota(snapshot_dir)
    assert result.exceeded is False
    assert result.current == 1
    assert result.headroom == 2


def test_check_quota_exceeded_when_over_limit(snapshot_dir: Path) -> None:
    for name in ("a", "b", "c"):
        _write(snapshot_dir, name, {"K": name})
    set_quota(snapshot_dir, 2)
    result = check_quota(snapshot_dir)
    assert result.exceeded is True
    assert result.headroom == 0


def test_check_quota_excludes_quota_file_from_count(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "only", {"A": "1"})
    set_quota(snapshot_dir, 5)
    result = check_quota(snapshot_dir)
    assert result.current == 1
