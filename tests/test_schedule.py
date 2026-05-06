"""Tests for envforge.schedule."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.schedule import (
    ScheduleEntry,
    ScheduleSession,
    run_once,
    start_schedule,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snaps"
    d.mkdir()
    return d


def _no_sleep(seconds: float) -> None:  # noqa: ARG001
    pass


def test_run_once_creates_file(snapshot_dir: Path) -> None:
    env = {"FOO": "bar"}
    name = run_once(snapshot_dir, "mysnap", env=env)
    files = list(snapshot_dir.glob("mysnap_*.json"))
    assert len(files) == 1
    assert files[0].stem == name


def test_run_once_saves_env_vars(snapshot_dir: Path) -> None:
    env = {"KEY": "value"}
    name = run_once(snapshot_dir, "s", env=env)
    data = json.loads((snapshot_dir / f"{name}.json").read_text())
    assert data["KEY"] == "value"


def test_run_once_returns_versioned_name(snapshot_dir: Path) -> None:
    name = run_once(snapshot_dir, "snap", env={})
    assert name.startswith("snap_")


def test_start_schedule_returns_session(snapshot_dir: Path) -> None:
    session = start_schedule(
        snapshot_dir, "s", interval_seconds=1, max_runs=1,
        env={}, _sleep=_no_sleep,
    )
    assert isinstance(session, ScheduleSession)


def test_start_schedule_run_count(snapshot_dir: Path) -> None:
    session = start_schedule(
        snapshot_dir, "s", interval_seconds=1, max_runs=3,
        env={}, _sleep=_no_sleep,
    )
    assert session.entries[0].run_count == 3


def test_start_schedule_creates_multiple_files(snapshot_dir: Path) -> None:
    start_schedule(
        snapshot_dir, "multi", interval_seconds=1, max_runs=3,
        env={"A": "1"}, _sleep=_no_sleep,
    )
    files = list(snapshot_dir.glob("multi_*.json"))
    assert len(files) == 3


def test_start_schedule_calls_on_snapshot(snapshot_dir: Path) -> None:
    calls: list[str] = []
    start_schedule(
        snapshot_dir, "s", interval_seconds=1, max_runs=2,
        on_snapshot=calls.append, env={}, _sleep=_no_sleep,
    )
    assert len(calls) == 2


def test_start_schedule_sets_stopped_at(snapshot_dir: Path) -> None:
    session = start_schedule(
        snapshot_dir, "s", interval_seconds=1, max_runs=1,
        env={}, _sleep=_no_sleep,
    )
    assert session.stopped_at is not None


def test_start_schedule_entry_has_last_run(snapshot_dir: Path) -> None:
    session = start_schedule(
        snapshot_dir, "s", interval_seconds=1, max_runs=1,
        env={}, _sleep=_no_sleep,
    )
    assert session.entries[0].last_run is not None
