"""Watch for environment variable changes and record diffs over time."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from envforge.diff import diff_dicts, DiffResult
from envforge.snapshot import capture, save


@dataclass
class WatchEvent:
    timestamp: float
    snapshot_name: str
    diff: DiffResult


@dataclass
class WatchSession:
    events: list[WatchEvent] = field(default_factory=list)
    baseline: dict[str, str] = field(default_factory=dict)


def start_watch(
    snapshot_dir: Path,
    interval: float = 5.0,
    iterations: int = 0,
    on_change: Optional[Callable[[WatchEvent], None]] = None,
    env: Optional[dict[str, str]] = None,
) -> WatchSession:
    """Poll environment variables and record snapshots when changes are detected.

    Args:
        snapshot_dir: Directory where snapshots are stored.
        interval: Seconds between polls.
        iterations: Number of polls (0 = run forever, useful for testing).
        on_change: Optional callback invoked with a WatchEvent on each change.
        env: Override environment dict (defaults to os.environ).

    Returns:
        A WatchSession containing all recorded events.
    """
    session = WatchSession()
    session.baseline = capture(env)
    counter = 0

    while True:
        time.sleep(interval)
        current = capture(env)
        result = diff_dicts(session.baseline, current)

        if not result.is_empty():
            ts = time.time()
            name = f"watch_{int(ts)}"
            save(current, name, snapshot_dir)
            event = WatchEvent(timestamp=ts, snapshot_name=name, diff=result)
            session.events.append(event)
            if on_change:
                on_change(event)
            session.baseline = current

        counter += 1
        if iterations and counter >= iterations:
            break

    return session


def session_summary(session: WatchSession) -> str:
    """Return a human-readable summary of a watch session."""
    if not session.events:
        return "No changes detected during watch session."
    lines = [f"Watch session recorded {len(session.events)} change(s):"]
    for evt in session.events:
        lines.append(f"  [{evt.snapshot_name}] {evt.diff.summary()}")
    return "\n".join(lines)
