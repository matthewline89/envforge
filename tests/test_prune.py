"""Tests for envforge.prune."""
from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envforge.prune import prune_by_age, prune_by_count, PruneResult


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(directory: Path, name: str, env: dict | None = None) -> Path:
    path = directory / f"{name}.json"
    path.write_text(json.dumps(env or {"KEY": "val"}))
    return path


# ---------------------------------------------------------------------------
# prune_by_count
# ---------------------------------------------------------------------------

def test_prune_by_count_returns_prune_result(snapshot_dir):
    _write(snapshot_dir, "snap1")
    _write(snapshot_dir, "snap2")
    result = prune_by_count(snapshot_dir, keep=2)
    assert isinstance(result, PruneResult)


def test_prune_by_count_keeps_most_recent(snapshot_dir):
    p1 = _write(snapshot_dir, "snap1")
    time.sleep(0.02)
    p2 = _write(snapshot_dir, "snap2")
    time.sleep(0.02)
    _write(snapshot_dir, "snap3")

    result = prune_by_count(snapshot_dir, keep=2)
    assert "snap1" in result.removed
    assert "snap2" in result.kept
    assert "snap3" in result.kept


def test_prune_by_count_removes_correct_number(snapshot_dir):
    for i in range(5):
        _write(snapshot_dir, f"snap{i}")
        time.sleep(0.01)

    result = prune_by_count(snapshot_dir, keep=3)
    assert result.total_removed == 2
    assert len(result.kept) == 3


def test_prune_by_count_nothing_removed_when_under_limit(snapshot_dir):
    _write(snapshot_dir, "snap1")
    result = prune_by_count(snapshot_dir, keep=10)
    assert result.total_removed == 0
    assert "snap1" in result.kept


def test_prune_by_count_raises_for_zero_keep(snapshot_dir):
    with pytest.raises(ValueError, match="keep must be"):
        prune_by_count(snapshot_dir, keep=0)


def test_prune_by_count_deletes_files(snapshot_dir):
    p1 = _write(snapshot_dir, "old")
    time.sleep(0.02)
    _write(snapshot_dir, "new")

    prune_by_count(snapshot_dir, keep=1)
    assert not p1.exists()


# ---------------------------------------------------------------------------
# prune_by_age
# ---------------------------------------------------------------------------

def test_prune_by_age_returns_prune_result(snapshot_dir):
    _write(snapshot_dir, "snap1")
    now = datetime.now(tz=timezone.utc)
    result = prune_by_age(snapshot_dir, max_age_days=30, now=now)
    assert isinstance(result, PruneResult)


def test_prune_by_age_removes_old_snapshot(snapshot_dir):
    path = _write(snapshot_dir, "ancient")
    # Simulate "now" being far in the future
    future = datetime.now(tz=timezone.utc) + timedelta(days=100)
    result = prune_by_age(snapshot_dir, max_age_days=1, now=future)
    assert "ancient" in result.removed
    assert not path.exists()


def test_prune_by_age_keeps_recent_snapshot(snapshot_dir):
    _write(snapshot_dir, "fresh")
    now = datetime.now(tz=timezone.utc)
    result = prune_by_age(snapshot_dir, max_age_days=30, now=now)
    assert "fresh" in result.kept
    assert result.total_removed == 0


def test_prune_by_age_raises_for_non_positive_age(snapshot_dir):
    with pytest.raises(ValueError, match="max_age_days must be"):
        prune_by_age(snapshot_dir, max_age_days=0)


def test_prune_by_age_excludes_metadata_files(snapshot_dir):
    _write(snapshot_dir, "tags")  # tags.json — should be excluded
    future = datetime.now(tz=timezone.utc) + timedelta(days=999)
    result = prune_by_age(snapshot_dir, max_age_days=1, now=future)
    assert "tags" not in result.removed
