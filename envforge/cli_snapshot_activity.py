"""CLI commands for snapshot activity tracking."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_activity import clear_activity, get_activity, record_activity


@click.group("activity")
def activity_group() -> None:
    """Track snapshot read/write/delete activity."""


@activity_group.command("record")
@click.argument("snapshot")
@click.argument("action", type=click.Choice(["read", "write", "delete"]))
@click.option("--user", default=None, help="User performing the action.")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def record_cmd(snapshot: str, action: str, user: str | None, snap_dir: str) -> None:
    """Record an activity event for SNAPSHOT."""
    entry = record_activity(Path(snap_dir), snapshot, action, user=user)
    click.echo(f"Recorded {entry.action!r} for '{entry.snapshot}' at {entry.timestamp}")


@activity_group.command("log")
@click.argument("snapshot", required=False, default=None)
@click.option("--action", default=None, help="Filter by action type.")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def log_cmd(snapshot: str | None, action: str | None, snap_dir: str) -> None:
    """Show activity log, optionally filtered by SNAPSHOT and/or action."""
    report = get_activity(Path(snap_dir), snapshot=snapshot)
    if action:
        report = report.by_action(action)
    if report.is_empty():
        click.echo("No activity recorded.")
        return
    for entry in report.entries:
        user_part = f" [{entry.user}]" if entry.user else ""
        click.echo(f"{entry.timestamp}  {entry.action:<8}  {entry.snapshot}{user_part}")


@activity_group.command("clear")
@click.argument("snapshot", required=False, default=None)
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def clear_cmd(snapshot: str | None, snap_dir: str) -> None:
    """Clear activity log for SNAPSHOT, or all activity if omitted."""
    removed = clear_activity(Path(snap_dir), snapshot=snapshot)
    target = f"'{snapshot}'" if snapshot else "all snapshots"
    click.echo(f"Cleared {removed} activity record(s) for {target}.")
