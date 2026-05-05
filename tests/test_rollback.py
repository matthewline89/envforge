"""Tests for envforge.rollback."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.rollback import (
    RollbackError,
    RollbackResult,
    list_rollback_points,
    rollback,
)
from envforge.snapshot import save


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def _save_with_history(name: str, vars_: dict, snapshot_dir: Path) -> None:
    """Save a snapshot and record a history entry manually."""
    from envforge.history import record_event

    save(name, vars_, snapshot_dir)
    record_event(name, event="save", snapshot_dir=snapshot_dir, vars=vars_)


# ---------------------------------------------------------------------------
# list_rollback_points
# ---------------------------------------------------------------------------


def test_list_rollback_points_returns_empty_for_unknown_snapshot(snapshot_dir: Path) -> None:
    points = list_rollback_points("ghost", snapshot_dir)
    assert points == []


def test_list_rollback_points_returns_entries_with_vars(snapshot_dir: Path) -> None:
    _save_with_history("dev", {"A": "1"}, snapshot_dir)
    _save_with_history("dev", {"A": "2"}, snapshot_dir)
    points = list_rollback_points("dev", snapshot_dir)
    assert len(points) == 2


def test_list_rollback_points_excludes_other_snapshots(snapshot_dir: Path) -> None:
    _save_with_history("dev", {"A": "1"}, snapshot_dir)
    _save_with_history("prod", {"B": "2"}, snapshot_dir)
    points = list_rollback_points("dev", snapshot_dir)
    assert all(p["snapshot"] == "dev" for p in points)
    assert len(points) == 1


# ---------------------------------------------------------------------------
# rollback
# ---------------------------------------------------------------------------


def test_rollback_raises_when_not_enough_history(snapshot_dir: Path) -> None:
    _save_with_history("dev", {"A": "1"}, snapshot_dir)
    with pytest.raises(RollbackError, match="Not enough history"):
        rollback("dev", snapshot_dir, steps=1)


def test_rollback_raises_for_zero_steps(snapshot_dir: Path) -> None:
    with pytest.raises(RollbackError, match="steps must be >= 1"):
        rollback("dev", snapshot_dir, steps=0)


def test_rollback_returns_rollback_result(snapshot_dir: Path) -> None:
    _save_with_history("dev", {"A": "1"}, snapshot_dir)
    _save_with_history("dev", {"A": "2"}, snapshot_dir)
    result = rollback("dev", snapshot_dir, steps=1)
    assert isinstance(result, RollbackResult)
    assert result.snapshot_name == "dev"


def test_rollback_restores_previous_vars(snapshot_dir: Path) -> None:
    _save_with_history("dev", {"A": "1"}, snapshot_dir)
    _save_with_history("dev", {"A": "2"}, snapshot_dir)
    result = rollback("dev", snapshot_dir, steps=1)
    assert result.rolled_back_vars == {"A": "1"}
    assert result.previous_vars == {"A": "2"}


def test_rollback_writes_snapshot_file(snapshot_dir: Path) -> None:
    _save_with_history("dev", {"X": "old"}, snapshot_dir)
    _save_with_history("dev", {"X": "new"}, snapshot_dir)
    rollback("dev", snapshot_dir, steps=1)
    snap_file = snapshot_dir / "dev.json"
    data = json.loads(snap_file.read_text())
    assert data["X"] == "old"


def test_rollback_records_history_entry(snapshot_dir: Path) -> None:
    from envforge.history import get_history

    _save_with_history("dev", {"K": "v1"}, snapshot_dir)
    _save_with_history("dev", {"K": "v2"}, snapshot_dir)
    rollback("dev", snapshot_dir, steps=1)
    history = get_history(snapshot_dir)
    events = [e["event"] for e in history if e.get("snapshot") == "dev"]
    assert "rollback" in events
