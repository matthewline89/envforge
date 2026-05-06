"""CLI commands for managing triggers."""

from __future__ import annotations

from pathlib import Path

import click

from envforge.trigger import (
    TriggerEntry,
    add_trigger,
    list_triggers,
    remove_trigger,
)

DEFAULT_DIR = Path.home() / ".envforge"
VALID_CONDITIONS = ("key_added", "key_removed", "value_changed")


@click.group("trigger")
def trigger_group() -> None:
    """Manage auto-snapshot triggers."""


@trigger_group.command("add")
@click.argument("name")
@click.option(
    "--condition",
    required=True,
    type=click.Choice(VALID_CONDITIONS),
    help="Condition that fires the trigger.",
)
@click.option("--key", default=None, help="Specific env key to watch (optional).")
@click.option("--prefix", default="trigger", show_default=True,
              help="Snapshot name prefix.")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def add_cmd(name: str, condition: str, key: str | None, prefix: str, snap_dir: str) -> None:
    """Register a new trigger."""
    d = Path(snap_dir)
    d.mkdir(parents=True, exist_ok=True)
    entry = TriggerEntry(name=name, condition=condition,
                         target_key=key, snapshot_prefix=prefix)
    is_new = add_trigger(d, entry)
    status = "Added" if is_new else "Updated"
    click.echo(f"{status} trigger '{name}' (condition: {condition}).")


@trigger_group.command("remove")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def remove_cmd(name: str, snap_dir: str) -> None:
    """Remove a trigger by name."""
    d = Path(snap_dir)
    if remove_trigger(d, name):
        click.echo(f"Removed trigger '{name}'.")
    else:
        click.echo(f"Trigger '{name}' not found.", err=True)
        raise SystemExit(1)


@trigger_group.command("list")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def list_cmd(snap_dir: str) -> None:
    """List all registered triggers."""
    d = Path(snap_dir)
    entries = list_triggers(d)
    if not entries:
        click.echo("No triggers registered.")
        return
    for e in entries:
        key_info = f" (key: {e.target_key})" if e.target_key else ""
        click.echo(f"  {e.name}: {e.condition}{key_info} -> prefix '{e.snapshot_prefix}'")
