"""Rollback support: revert a snapshot directory to a previous history entry."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from envforge.history import get_history, record_event
from envforge.snapshot import load, save


@dataclass
class RollbackError(Exception):
    message: str

    def __str__(self) -> str:
        return self.message


@dataclass
class RollbackResult:
    snapshot_name: str
    restored_from_event: str
    previous_vars: dict[str, str]
    rolled_back_vars: dict[str, str]


def list_rollback_points(
    snapshot_name: str,
    snapshot_dir: Path,
) -> list[dict]:
    """Return history entries for *snapshot_name* that can be rolled back to."""
    history = get_history(snapshot_dir)
    return [
        entry
        for entry in history
        if entry.get("snapshot") == snapshot_name and "vars" in entry
    ]


def rollback(
    snapshot_name: str,
    snapshot_dir: Path,
    steps: int = 1,
    note: Optional[str] = None,
) -> RollbackResult:
    """Roll back *snapshot_name* by *steps* save events.

    Raises RollbackError if there are not enough history entries to roll back.
    """
    if steps < 1:
        raise RollbackError("steps must be >= 1")

    points = list_rollback_points(snapshot_name, snapshot_dir)

    if len(points) < steps + 1:
        raise RollbackError(
            f"Not enough history to roll back {steps} step(s) for '{snapshot_name}'. "
            f"Found {len(points)} rollback point(s)."
        )

    # points are oldest-first; target is *steps* entries before the last
    target_entry = points[-(steps + 1)]
    current_vars = load(snapshot_name, snapshot_dir)
    target_vars: dict[str, str] = target_entry["vars"]

    save(snapshot_name, target_vars, snapshot_dir)
    record_event(
        snapshot_name,
        event="rollback",
        snapshot_dir=snapshot_dir,
        vars=target_vars,
        note=note or f"Rolled back {steps} step(s)",
    )

    return RollbackResult(
        snapshot_name=snapshot_name,
        restored_from_event=target_entry.get("timestamp", "unknown"),
        previous_vars=current_vars,
        rolled_back_vars=target_vars,
    )
