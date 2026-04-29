"""CLI commands for managing snapshot aliases."""

from __future__ import annotations

from pathlib import Path

import click

from envforge.alias import (
    list_aliases,
    remove_alias,
    resolve_alias,
    set_alias,
)

DEFAULT_DIR = Path.home() / ".envforge" / "snapshots"


@click.group("alias")
def alias_group() -> None:
    """Manage snapshot aliases."""


@alias_group.command("set")
@click.argument("alias")
@click.argument("snapshot")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def set_cmd(alias: str, snapshot: str, snap_dir: str) -> None:
    """Create or update ALIAS pointing to SNAPSHOT."""
    set_alias(Path(snap_dir), alias, snapshot)
    click.echo(f"Alias '{alias}' -> '{snapshot}' saved.")


@alias_group.command("remove")
@click.argument("alias")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def remove_cmd(alias: str, snap_dir: str) -> None:
    """Remove ALIAS."""
    removed = remove_alias(Path(snap_dir), alias)
    if removed:
        click.echo(f"Alias '{alias}' removed.")
    else:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)


@alias_group.command("list")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def list_cmd(snap_dir: str) -> None:
    """List all aliases."""
    aliases = list_aliases(Path(snap_dir))
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, snapshot in sorted(aliases.items()):
        click.echo(f"{alias:20s} -> {snapshot}")


@alias_group.command("resolve")
@click.argument("alias")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def resolve_cmd(alias: str, snap_dir: str) -> None:
    """Print the snapshot name that ALIAS points to."""
    target = resolve_alias(Path(snap_dir), alias)
    if target is None:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)
    click.echo(target)
