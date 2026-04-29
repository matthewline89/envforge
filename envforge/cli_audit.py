"""CLI commands for the audit log."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.audit import clear_audit_log, get_audit_log, record_action

_DEFAULT_DIR = Path.home() / ".envforge" / "snapshots"


@click.group("audit")
def audit_group() -> None:
    """View and manage the envforge audit log."""


@audit_group.command("log")
@click.option("--snapshot", default=None, help="Filter by snapshot name.")
@click.option("--action", default=None, help="Filter by action type.")
@click.option("--dir", "snapshot_dir", default=str(_DEFAULT_DIR), show_default=True)
def log_cmd(snapshot: str, action: str, snapshot_dir: str) -> None:
    """List audit log entries."""
    entries = get_audit_log(Path(snapshot_dir), snapshot=snapshot, action=action)
    if not entries:
        click.echo("No audit entries found.")
        return
    for e in entries:
        note_part = f"  # {e.note}" if e.note else ""
        click.echo(f"[{e.timestamp}] {e.user} {e.action} {e.snapshot}{note_part}")


@audit_group.command("record")
@click.argument("action")
@click.argument("snapshot")
@click.option("--note", default=None, help="Optional note to attach.")
@click.option("--user", default=None, help="Override detected user.")
@click.option("--dir", "snapshot_dir", default=str(_DEFAULT_DIR), show_default=True)
def record_cmd(action: str, snapshot: str, note: str, user: str, snapshot_dir: str) -> None:
    """Manually record an audit event."""
    entry = record_action(Path(snapshot_dir), action, snapshot, note=note, user=user)
    click.echo(f"Recorded: {entry.action} on '{entry.snapshot}' by {entry.user}")


@audit_group.command("clear")
@click.option("--dir", "snapshot_dir", default=str(_DEFAULT_DIR), show_default=True)
@click.confirmation_option(prompt="Clear all audit entries?")
def clear_cmd(snapshot_dir: str) -> None:
    """Remove all audit log entries."""
    removed = clear_audit_log(Path(snapshot_dir))
    click.echo(f"Cleared {removed} audit entries.")
