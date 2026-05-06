"""CLI commands for snapshot set management."""

from __future__ import annotations

import click
from pathlib import Path

from envforge.snapshot_set import (
    create_set,
    delete_set,
    get_set,
    list_sets,
    add_to_set,
    remove_from_set,
    SnapshotSetError,
)

_DEFAULT_DIR = Path.home() / ".envforge"


@click.group(name="set")
def set_group():
    """Manage named snapshot sets."""


@set_group.command(name="create")
@click.argument("name")
@click.argument("members", nargs=-1, required=True)
@click.option("--dir", "snapshot_dir", default=str(_DEFAULT_DIR), show_default=True)
def create_cmd(name: str, members: tuple, snapshot_dir: str):
    """Create a named set containing MEMBERS snapshots."""
    d = Path(snapshot_dir)
    d.mkdir(parents=True, exist_ok=True)
    is_new = create_set(d, name, list(members))
    verb = "Created" if is_new else "Updated"
    click.echo(f"{verb} set '{name}' with {len(members)} member(s).")


@set_group.command(name="delete")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=str(_DEFAULT_DIR), show_default=True)
def delete_cmd(name: str, snapshot_dir: str):
    """Delete a named snapshot set."""
    removed = delete_set(Path(snapshot_dir), name)
    if removed:
        click.echo(f"Deleted set '{name}'.")
    else:
        click.echo(f"Set '{name}' not found.", err=True)


@set_group.command(name="show")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=str(_DEFAULT_DIR), show_default=True)
def show_cmd(name: str, snapshot_dir: str):
    """Show members of a named snapshot set."""
    members = get_set(Path(snapshot_dir), name)
    if members is None:
        click.echo(f"Set '{name}' not found.", err=True)
        return
    if not members:
        click.echo(f"Set '{name}' is empty.")
        return
    for m in members:
        click.echo(m)


@set_group.command(name="list")
@click.option("--dir", "snapshot_dir", default=str(_DEFAULT_DIR), show_default=True)
def list_cmd(snapshot_dir: str):
    """List all snapshot sets."""
    all_sets = list_sets(Path(snapshot_dir))
    if not all_sets:
        click.echo("No snapshot sets defined.")
        return
    for name, members in all_sets.items():
        click.echo(f"{name} ({len(members)} member(s))")


@set_group.command(name="add")
@click.argument("name")
@click.argument("snapshot")
@click.option("--dir", "snapshot_dir", default=str(_DEFAULT_DIR), show_default=True)
def add_cmd(name: str, snapshot: str, snapshot_dir: str):
    """Add SNAPSHOT to an existing set."""
    try:
        added = add_to_set(Path(snapshot_dir), name, snapshot)
        if added:
            click.echo(f"Added '{snapshot}' to set '{name}'.")
        else:
            click.echo(f"'{snapshot}' is already in set '{name}'.")
    except SnapshotSetError as exc:
        click.echo(str(exc), err=True)


@set_group.command(name="remove")
@click.argument("name")
@click.argument("snapshot")
@click.option("--dir", "snapshot_dir", default=str(_DEFAULT_DIR), show_default=True)
def remove_cmd(name: str, snapshot: str, snapshot_dir: str):
    """Remove SNAPSHOT from a set."""
    removed = remove_from_set(Path(snapshot_dir), name, snapshot)
    if removed:
        click.echo(f"Removed '{snapshot}' from set '{name}'.")
    else:
        click.echo(f"'{snapshot}' was not in set '{name}'.", err=True)
