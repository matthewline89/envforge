"""CLI commands for snapshot group management."""
from __future__ import annotations

import click
from pathlib import Path

from envforge import group as grp

DEFAULT_DIR = Path.home() / ".envforge"


@click.group("group")
def group_group() -> None:
    """Manage snapshot groups."""


@group_group.command("add")
@click.argument("group")
@click.argument("snapshot")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def add_cmd(group: str, snapshot: str, snap_dir: str) -> None:
    """Add SNAPSHOT to GROUP."""
    d = Path(snap_dir)
    d.mkdir(parents=True, exist_ok=True)
    added = grp.add_to_group(d, group, snapshot)
    if added:
        click.echo(f"Added '{snapshot}' to group '{group}'.")
    else:
        click.echo(f"'{snapshot}' is already in group '{group}'.")


@group_group.command("remove")
@click.argument("group")
@click.argument("snapshot")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def remove_cmd(group: str, snapshot: str, snap_dir: str) -> None:
    """Remove SNAPSHOT from GROUP."""
    removed = grp.remove_from_group(Path(snap_dir), group, snapshot)
    if removed:
        click.echo(f"Removed '{snapshot}' from group '{group}'.")
    else:
        click.echo(f"'{snapshot}' was not found in group '{group}'.")


@group_group.command("list")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def list_cmd(snap_dir: str) -> None:
    """List all groups and their members."""
    groups = grp.list_groups(Path(snap_dir))
    if not groups:
        click.echo("No groups defined.")
        return
    for name, members in sorted(groups.items()):
        click.echo(f"{name}: {', '.join(members)}")


@group_group.command("show")
@click.argument("group")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def show_cmd(group: str, snap_dir: str) -> None:
    """Show members of GROUP."""
    members = grp.get_group(Path(snap_dir), group)
    if members is None:
        click.echo(f"Group '{group}' does not exist.")
        return
    if not members:
        click.echo(f"Group '{group}' is empty.")
        return
    for m in members:
        click.echo(m)


@group_group.command("delete")
@click.argument("group")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def delete_cmd(group: str, snap_dir: str) -> None:
    """Delete an entire GROUP."""
    deleted = grp.delete_group(Path(snap_dir), group)
    if deleted:
        click.echo(f"Deleted group '{group}'.")
    else:
        click.echo(f"Group '{group}' does not exist.")
