"""CLI commands for snapshot reminders."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_reminder import (
    add_reminder,
    get_reminders,
    remove_reminder,
)

DEFAULT_DIR = Path(".envforge")


@click.group("reminder")
def reminder_group() -> None:
    """Manage snapshot reminders."""


@reminder_group.command("add")
@click.argument("snapshot")
@click.argument("due")  # ISO date, e.g. 2025-12-31
@click.argument("message")
@click.option("--recur", default=None, help="Recurrence: daily, weekly, monthly")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR))
def add_cmd(snapshot: str, due: str, message: str, recur: str | None, snap_dir: str) -> None:
    """Add a reminder for SNAPSHOT due on DUE with MESSAGE."""
    d = Path(snap_dir)
    d.mkdir(parents=True, exist_ok=True)
    created = add_reminder(d, snapshot, message, due, recur=recur)
    if created:
        click.echo(f"Reminder added for '{snapshot}' due {due}.")
    else:
        click.echo(f"Reminder already exists for '{snapshot}' on {due}.")


@reminder_group.command("remove")
@click.argument("snapshot")
@click.argument("due")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR))
def remove_cmd(snapshot: str, due: str, snap_dir: str) -> None:
    """Remove reminder for SNAPSHOT on DUE date."""
    d = Path(snap_dir)
    removed = remove_reminder(d, snapshot, due)
    if removed:
        click.echo(f"Reminder removed for '{snapshot}' on {due}.")
    else:
        click.echo(f"No reminder found for '{snapshot}' on {due}.")


@reminder_group.command("list")
@click.option("--snapshot", default=None, help="Filter by snapshot name")
@click.option("--due-before", "due_before", default=None, help="Show only reminders due before this ISO date")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR))
def list_cmd(snapshot: str | None, due_before: str | None, snap_dir: str) -> None:
    """List reminders, optionally filtered."""
    d = Path(snap_dir)
    report = get_reminders(d)
    entries = report.entries
    if snapshot:
        entries = [e for e in entries if e.snapshot == snapshot]
    if due_before:
        entries = [e for e in entries if e.due <= due_before]
    if not entries:
        click.echo("No reminders found.")
        return
    for entry in entries:
        recur_str = f" [{entry.recur}]" if entry.recur else ""
        click.echo(f"{entry.due}{recur_str}  {entry.snapshot}: {entry.message}")
