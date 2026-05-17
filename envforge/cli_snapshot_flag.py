"""CLI commands for snapshot flag management."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_flag import (
    clear_flags,
    find_by_flag,
    get_flags,
    has_flag,
    remove_flag,
    set_flag,
)

DEFAULT_DIR = Path(".envforge")


@click.group("flag")
def flag_group() -> None:
    """Manage boolean flags on snapshots."""


@flag_group.command("set")
@click.argument("name")
@click.argument("flag")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def set_cmd(name: str, flag: str, snap_dir: str) -> None:
    """Attach FLAG to snapshot NAME."""
    added = set_flag(Path(snap_dir), name, flag)
    if added:
        click.echo(f"Flag '{flag}' set on '{name}'.")
    else:
        click.echo(f"Flag '{flag}' already set on '{name}'.")


@flag_group.command("remove")
@click.argument("name")
@click.argument("flag")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def remove_cmd(name: str, flag: str, snap_dir: str) -> None:
    """Remove FLAG from snapshot NAME."""
    removed = remove_flag(Path(snap_dir), name, flag)
    if removed:
        click.echo(f"Flag '{flag}' removed from '{name}'.")
    else:
        click.echo(f"Flag '{flag}' not found on '{name}'.")


@flag_group.command("show")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def show_cmd(name: str, snap_dir: str) -> None:
    """List all flags on snapshot NAME."""
    flags = get_flags(Path(snap_dir), name)
    if not flags:
        click.echo(f"No flags set on '{name}'.")
    else:
        for f in flags:
            click.echo(f)


@flag_group.command("find")
@click.argument("flag")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def find_cmd(flag: str, snap_dir: str) -> None:
    """Find all snapshots that carry FLAG."""
    names = find_by_flag(Path(snap_dir), flag)
    if not names:
        click.echo(f"No snapshots carry flag '{flag}'.")
    else:
        for n in names:
            click.echo(n)


@flag_group.command("clear")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def clear_cmd(name: str, snap_dir: str) -> None:
    """Remove all flags from snapshot NAME."""
    count = clear_flags(Path(snap_dir), name)
    click.echo(f"Cleared {count} flag(s) from '{name}'.")
