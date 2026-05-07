"""CLI commands for snapshot slots."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.slot import list_slots, remove_slot, resolve_slot, set_slot

_DEFAULT_DIR = Path.home() / ".envforge"


@click.group("slot")
def slot_group() -> None:
    """Manage named snapshot slots."""


@slot_group.command("set")
@click.argument("slot")
@click.argument("snapshot_name")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def set_cmd(slot: str, snapshot_name: str, snap_dir: str) -> None:
    """Assign SNAPSHOT_NAME to SLOT."""
    d = Path(snap_dir)
    d.mkdir(parents=True, exist_ok=True)
    is_new = set_slot(d, slot, snapshot_name)
    verb = "Created" if is_new else "Updated"
    click.echo(f"{verb} slot '{slot}' → '{snapshot_name}'")


@slot_group.command("remove")
@click.argument("slot")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def remove_cmd(slot: str, snap_dir: str) -> None:
    """Remove SLOT."""
    d = Path(snap_dir)
    if remove_slot(d, slot):
        click.echo(f"Removed slot '{slot}'.")
    else:
        click.echo(f"Slot '{slot}' not found.", err=True)


@slot_group.command("resolve")
@click.argument("slot")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def resolve_cmd(slot: str, snap_dir: str) -> None:
    """Print the snapshot name assigned to SLOT."""
    name = resolve_slot(Path(snap_dir), slot)
    if name is None:
        click.echo(f"No snapshot assigned to slot '{slot}'.", err=True)
    else:
        click.echo(name)


@slot_group.command("list")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def list_cmd(snap_dir: str) -> None:
    """List all slots and their assigned snapshots."""
    slots = list_slots(Path(snap_dir))
    if not slots:
        click.echo("No slots defined.")
        return
    for slot, name in sorted(slots.items()):
        click.echo(f"{slot}: {name}")
