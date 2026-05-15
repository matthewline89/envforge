"""CLI commands for snapshot metadata management."""
from __future__ import annotations

import json
from pathlib import Path

import click

from envforge.snapshot_meta import (
    get_all_meta,
    get_meta,
    list_meta_snapshots,
    remove_meta,
    set_meta,
)

DEFAULT_DIR = Path.home() / ".envforge"


@click.group(name="meta")
def meta_group() -> None:
    """Manage arbitrary metadata attached to snapshots."""


@meta_group.command(name="set")
@click.argument("name")
@click.argument("key")
@click.argument("value")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def set_cmd(name: str, key: str, value: str, snap_dir: str) -> None:
    """Set a metadata KEY=VALUE for snapshot NAME."""
    d = Path(snap_dir)
    d.mkdir(parents=True, exist_ok=True)
    is_new = set_meta(d, name, key, value)
    verb = "Set" if is_new else "Updated"
    click.echo(f"{verb} meta [{key}] on '{name}'.")


@meta_group.command(name="get")
@click.argument("name")
@click.argument("key")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def get_cmd(name: str, key: str, snap_dir: str) -> None:
    """Get a single metadata KEY for snapshot NAME."""
    val = get_meta(Path(snap_dir), name, key)
    if val is None:
        click.echo(f"No meta key '{key}' for '{name}'.")
    else:
        click.echo(str(val))


@meta_group.command(name="remove")
@click.argument("name")
@click.argument("key")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def remove_cmd(name: str, key: str, snap_dir: str) -> None:
    """Remove a metadata KEY from snapshot NAME."""
    removed = remove_meta(Path(snap_dir), name, key)
    if removed:
        click.echo(f"Removed meta key '{key}' from '{name}'.")
    else:
        click.echo(f"Meta key '{key}' not found on '{name}'.")


@meta_group.command(name="show")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def show_cmd(name: str, snap_dir: str) -> None:
    """Show all metadata for snapshot NAME."""
    data = get_all_meta(Path(snap_dir), name)
    if not data:
        click.echo(f"No metadata for '{name}'.")
    else:
        click.echo(json.dumps(data, indent=2))


@meta_group.command(name="list")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def list_cmd(snap_dir: str) -> None:
    """List snapshots that have metadata."""
    names = list_meta_snapshots(Path(snap_dir))
    if not names:
        click.echo("No snapshots with metadata.")
    else:
        for n in names:
            click.echo(n)
