"""Schedule automatic snapshots at regular intervals."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from envforge.snapshot import capture, save
from envforge.history import record_event


@dataclass
class ScheduleEntry:
    snapshot_name: str
    interval_seconds: int
    last_run: Optional[str] = None
    run_count: int = 0


@dataclass
class ScheduleSession:
    entries: list[ScheduleEntry] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    stopped_at: Optional[str] = None


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def run_once(
    snapshot_dir: Path,
    snapshot_name: str,
    env: Optional[dict] = None,
) -> str:
    """Capture and save a snapshot immediately; return the saved filename."""
    data = capture(env=env)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    versioned_name = f"{snapshot_name}_{ts}"
    save(snapshot_dir, versioned_name, data)
    record_event(snapshot_dir, versioned_name, "scheduled_snapshot")
    return versioned_name


def start_schedule(
    snapshot_dir: Path,
    snapshot_name: str,
    interval_seconds: int,
    max_runs: int = 0,
    on_snapshot: Optional[Callable[[str], None]] = None,
    env: Optional[dict] = None,
    _sleep: Callable[[float], None] = time.sleep,
) -> ScheduleSession:
    """Run scheduled snapshots; blocks until max_runs reached (0 = run once)."""
    session = ScheduleSession()
    entry = ScheduleEntry(
        snapshot_name=snapshot_name,
        interval_seconds=interval_seconds,
    )
    session.entries.append(entry)

    runs = max(max_runs, 1)
    for i in range(runs):
        name = run_once(snapshot_dir, snapshot_name, env=env)
        entry.last_run = _now_iso()
        entry.run_count += 1
        if on_snapshot:
            on_snapshot(name)
        if i < runs - 1:
            _sleep(interval_seconds)

    session.stopped_at = _now_iso()
    return session
