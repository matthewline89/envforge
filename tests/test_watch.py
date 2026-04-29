"""Tests for envforge.watch."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch

import pytest

from envforge.watch import (
    WatchEvent,
    WatchSession,
    session_summary,
    start_watch,
)
from envforge.diff import DiffResult


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snaps"
    d.mkdir()
    return d


def _no_sleep(_: float) -> None:
    """Patch time.sleep to be a no-op."""


def test_start_watch_returns_session(snapshot_dir: Path) -> None:
    env = {"FOO": "bar"}
    with patch("envforge.watch.time.sleep", _no_sleep):
        session = start_watch(
            snapshot_dir=snapshot_dir,
            interval=0,
            iterations=1,
            env=env,
        )
    assert isinstance(session, WatchSession)


def test_no_change_produces_no_events(snapshot_dir: Path) -> None:
    env = {"FOO": "bar"}
    with patch("envforge.watch.time.sleep", _no_sleep):
        session = start_watch(
            snapshot_dir=snapshot_dir,
            interval=0,
            iterations=3,
            env=env,
        )
    assert session.events == []


def test_change_detected_calls_on_change(snapshot_dir: Path) -> None:
    envs = [{"FOO": "bar"}, {"FOO": "baz"}]
    call_count = 0

    def _capture(e):
        return e.copy() if e else {}

    captured_events: list[WatchEvent] = []

    def on_change(evt: WatchEvent) -> None:
        captured_events.append(evt)

    iter_env = iter(envs)

    with patch("envforge.watch.time.sleep", _no_sleep), \
         patch("envforge.watch.capture", side_effect=lambda e: next(iter_env).copy()):
        session = start_watch(
            snapshot_dir=snapshot_dir,
            interval=0,
            iterations=1,
            on_change=on_change,
        )

    assert len(captured_events) == 1
    assert captured_events[0].diff is not None


def test_session_summary_no_events() -> None:
    session = WatchSession()
    summary = session_summary(session)
    assert "No changes" in summary


def test_session_summary_with_events() -> None:
    diff = DiffResult(added={"NEW": "val"}, removed={}, changed={})
    event = WatchEvent(
        timestamp=time.time(),
        snapshot_name="watch_123",
        diff=diff,
    )
    session = WatchSession(events=[event], baseline={})
    summary = session_summary(session)
    assert "watch_123" in summary
    assert "1 change" in summary


def test_snapshot_saved_on_change(snapshot_dir: Path) -> None:
    envs = iter([{"A": "1"}, {"A": "2"}])

    with patch("envforge.watch.time.sleep", _no_sleep), \
         patch("envforge.watch.capture", side_effect=lambda e: next(envs).copy()), \
         patch("envforge.watch.time.time", return_value=9999.0):
        session = start_watch(
            snapshot_dir=snapshot_dir,
            interval=0,
            iterations=1,
        )

    assert len(session.events) == 1
    assert (snapshot_dir / "watch_9999.json").exists()
