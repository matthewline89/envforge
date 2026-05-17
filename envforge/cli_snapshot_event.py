"""CLI commands for snapshot event log."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_event import clear_events, get_event_log, record_event

DEFAULT_DIR = Path(".envforge")


@click.group("event")
def event_group() -> None:
    """Record and query snapshot events."""


@event_group.command("record")
@click.argument("snapshot")
@click.argument("event")
@click.option("--user", default=None, help="User performing the action.")
@click.option("--note", default=None, help="Optional note.")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR))
def record_cmd(snapshot: str, event: str, user: str, note: str, snap_dir: str) -> None:
    """Record an event for SNAPSHOT."""
    d = Path(snap_dir)
    d.mkdir(parents=True, exist_ok=True)
    entry = record_event(d, snapshot, event, user=user, note=note)
    click.echo(f"Recorded event '{entry.event}' for snapshot '{entry.snapshot}'.")


@event_group.command("log")
@click.argument("snapshot")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR))
def log_cmd(snapshot: str, snap_dir: str) -> None:
    """Show event log for SNAPSHOT."""
    log = get_event_log(Path(snap_dir))
    entries = log.for_snapshot(snapshot)
    if not entries:
        click.echo(f"No events recorded for '{snapshot}'.")
        return
    for e in entries:
        parts = [e.timestamp, e.event]
        if e.user:
            parts.append(f"user={e.user}")
        if e.note:
            parts.append(e.note)
        click.echo("  ".join(parts))


@event_group.command("clear")
@click.argument("snapshot")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR))
def clear_cmd(snapshot: str, snap_dir: str) -> None:
    """Clear all events for SNAPSHOT."""
    removed = clear_events(Path(snap_dir), snapshot=snapshot)
    click.echo(f"Cleared {removed} event(s) for '{snapshot}'.")
