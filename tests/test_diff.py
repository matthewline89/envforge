"""Tests for envforge.diff module."""

from __future__ import annotations

import pytest

from envforge.diff import DiffResult, diff_dicts, diff_snapshots
from envforge.snapshot import save


# ---------------------------------------------------------------------------
# DiffResult helpers
# ---------------------------------------------------------------------------

def test_diff_result_is_empty_when_no_changes():
    result = DiffResult()
    assert result.is_empty


def test_diff_result_not_empty_with_added():
    result = DiffResult(added={"FOO": "bar"})
    assert not result.is_empty


def test_summary_no_differences():
    assert DiffResult().summary() == "(no differences)"


def test_summary_contains_added_key():
    result = DiffResult(added={"NEW_VAR": "hello"})
    assert "+ NEW_VAR=hello" in result.summary()


def test_summary_contains_removed_key():
    result = DiffResult(removed={"OLD_VAR": "bye"})
    assert "- OLD_VAR=bye" in result.summary()


def test_summary_contains_changed_key():
    result = DiffResult(changed={"PORT": ("8000", "9000")})
    assert "~ PORT" in result.summary()
    assert "'8000'" in result.summary()
    assert "'9000'" in result.summary()


# ---------------------------------------------------------------------------
# diff_dicts
# ---------------------------------------------------------------------------

def test_diff_dicts_detects_added():
    result = diff_dicts({"A": "1"}, {"A": "1", "B": "2"})
    assert result.added == {"B": "2"}
    assert not result.removed
    assert not result.changed


def test_diff_dicts_detects_removed():
    result = diff_dicts({"A": "1", "B": "2"}, {"A": "1"})
    assert result.removed == {"B": "2"}


def test_diff_dicts_detects_changed():
    result = diff_dicts({"PORT": "8000"}, {"PORT": "9000"})
    assert result.changed == {"PORT": ("8000", "9000")}


def test_diff_dicts_identical_returns_empty():
    env = {"A": "1", "B": "2"}
    assert diff_dicts(env, env).is_empty


def test_diff_dicts_ignore_keys():
    result = diff_dicts({"SECRET": "old"}, {"SECRET": "new"}, ignore_keys=["SECRET"])
    assert result.is_empty


# ---------------------------------------------------------------------------
# diff_snapshots (integration)
# ---------------------------------------------------------------------------

@pytest.fixture()
def snapshot_dir(tmp_path):
    return str(tmp_path)


def test_diff_snapshots_detects_difference(snapshot_dir):
    save("snap_a", {"HOST": "localhost", "PORT": "5432"}, snapshot_dir=snapshot_dir)
    save("snap_b", {"HOST": "localhost", "PORT": "5433", "DEBUG": "1"}, snapshot_dir=snapshot_dir)

    result = diff_snapshots("snap_a", "snap_b", snapshot_dir=snapshot_dir)

    assert result.changed == {"PORT": ("5432", "5433")}
    assert result.added == {"DEBUG": "1"}
    assert not result.removed


def test_diff_snapshots_identical(snapshot_dir):
    env = {"A": "1"}
    save("snap_x", env, snapshot_dir=snapshot_dir)
    save("snap_y", env, snapshot_dir=snapshot_dir)

    assert diff_snapshots("snap_x", "snap_y", snapshot_dir=snapshot_dir).is_empty
