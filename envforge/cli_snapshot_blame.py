"""CLI commands for snapshot blame."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import click

from envforge.snapshot_blame import clear_blame, get_blame, record_blame


@click.group("blame")
def blame_group() -> None:
    """Track per-key authorship in snapshots."""


@blame_group.command("record")
@click.argument("snapshot_name")
@click.argument("key")
@click.argument("value")
@click.option("--user", required=True, help="User or process that set this key.")
@click.option("--note", default=None, help="Optional note about the change.")
@click.option(
    "--dir",
    "snapshot_dir",
    default=".envforge",
    show_default=True,
    help="Snapshot directory.",
)
def record_cmd(
    snapshot_name: str,
    key: str,
    value: str,
    user: str,
    note: str | None,
    snapshot_dir: str,
) -> None:
    """Record blame for a single key in a snapshot."""
    ts = datetime.now(timezone.utc).isoformat()
    entry = record_blame(
        Path(snapshot_dir), snapshot_name, key, value, user, ts, note
    )
    click.echo(f"Recorded: {entry.key} → {entry.user} at {entry.timestamp}")


@blame_group.command("show")
@click.argument("snapshot_name")
@click.option(
    "--dir",
    "snapshot_dir",
    default=".envforge",
    show_default=True,
    help="Snapshot directory.",
)
def show_cmd(snapshot_name: str, snapshot_dir: str) -> None:
    """Show blame information for all tracked keys in a snapshot."""
    report = get_blame(Path(snapshot_dir), snapshot_name)
    if not report.entries:
        click.echo(f"No blame records found for '{snapshot_name}'.")
        return
    for entry in sorted(report.entries, key=lambda e: e.key):
        note_part = f"  # {entry.note}" if entry.note else ""
        click.echo(f"  {entry.key}: {entry.user} @ {entry.timestamp}{note_part}")


@blame_group.command("clear")
@click.argument("snapshot_name")
@click.option(
    "--dir",
    "snapshot_dir",
    default=".envforge",
    show_default=True,
    help="Snapshot directory.",
)
def clear_cmd(snapshot_name: str, snapshot_dir: str) -> None:
    """Remove all blame records for a snapshot."""
    removed = clear_blame(Path(snapshot_dir), snapshot_name)
    if removed:
        click.echo(f"Cleared blame records for '{snapshot_name}'.")
    else:
        click.echo(f"No blame records found for '{snapshot_name}'.")
