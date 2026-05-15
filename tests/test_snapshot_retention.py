"""Tests for envforge.snapshot_retention."""
import pytest
from pathlib import Path

from envforge.snapshot_retention import (
    RetentionPolicy,
    RetentionResult,
    set_retention,
    get_retention,
    remove_retention,
    list_retention,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    snapshot_dir = tmp_path / "snapshots"
    snapshot_dir.mkdir()
    return snapshot_dir


def test_set_retention_creates_file(snapshot_dir):
    policy = RetentionPolicy(max_count=5)
    set_retention(snapshot_dir, "snap1", policy)
    assert (snapshot_dir / "retention.json").exists()


def test_set_retention_returns_true_when_new(snapshot_dir):
    policy = RetentionPolicy(max_count=3)
    assert set_retention(snapshot_dir, "snap1", policy) is True


def test_set_retention_returns_false_when_updated(snapshot_dir):
    policy = RetentionPolicy(max_count=3)
    set_retention(snapshot_dir, "snap1", policy)
    assert set_retention(snapshot_dir, "snap1", RetentionPolicy(max_count=10)) is False


def test_set_retention_stores_max_count(snapshot_dir):
    policy = RetentionPolicy(max_count=7)
    set_retention(snapshot_dir, "snap1", policy)
    result = get_retention(snapshot_dir, "snap1")
    assert result is not None
    assert result.max_count == 7


def test_set_retention_stores_max_age_days(snapshot_dir):
    policy = RetentionPolicy(max_age_days=30)
    set_retention(snapshot_dir, "snap1", policy)
    result = get_retention(snapshot_dir, "snap1")
    assert result is not None
    assert result.max_age_days == 30


def test_get_retention_returns_none_when_missing(snapshot_dir):
    assert get_retention(snapshot_dir, "nonexistent") is None


def test_remove_retention_returns_true_when_found(snapshot_dir):
    set_retention(snapshot_dir, "snap1", RetentionPolicy(max_count=5))
    assert remove_retention(snapshot_dir, "snap1") is True


def test_remove_retention_returns_false_when_missing(snapshot_dir):
    assert remove_retention(snapshot_dir, "ghost") is False


def test_remove_retention_clears_entry(snapshot_dir):
    set_retention(snapshot_dir, "snap1", RetentionPolicy(max_count=5))
    remove_retention(snapshot_dir, "snap1")
    assert get_retention(snapshot_dir, "snap1") is None


def test_list_retention_returns_all(snapshot_dir):
    set_retention(snapshot_dir, "a", RetentionPolicy(max_count=2))
    set_retention(snapshot_dir, "b", RetentionPolicy(max_age_days=14))
    result = list_retention(snapshot_dir)
    assert "a" in result
    assert "b" in result
    assert result["a"].max_count == 2
    assert result["b"].max_age_days == 14


def test_list_retention_empty_when_no_policies(snapshot_dir):
    assert list_retention(snapshot_dir) == {}


def test_retention_result_compliant_when_no_violations():
    policy = RetentionPolicy(max_count=5)
    result = RetentionResult(snapshot="snap1", policy=policy)
    assert result.compliant is True
    assert result.status == "compliant"


def test_retention_result_status_shows_violations():
    policy = RetentionPolicy(max_count=5, max_age_days=30)
    result = RetentionResult(
        snapshot="snap1",
        policy=policy,
        violates_count=True,
        violates_age=True,
    )
    assert result.compliant is False
    assert "exceeds max count" in result.status
    assert "exceeds max age" in result.status
