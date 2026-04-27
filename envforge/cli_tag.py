"""CLI commands for managing snapshot tags."""

from __future__ import annotations

from pathlib import Path

import click

from envforge import tag as tag_mod

DEFAULT_SNAPSHOT_DIR = Path.home() / ".envforge" / "snapshots"


@click.group(name="tag")
def tag_group() -> None:
    """Manage tags for snapshots."""


@tag_group.command(name="add")
@click.argument("tag")
@click.argument("snapshot")
@click.option("--dir", "snapshot_dir", default=str(DEFAULT_SNAPSHOT_DIR), show_default=True)
def add_cmd(tag: str, snapshot: str, snapshot_dir: str) -> None:
    """Tag SNAPSHOT with TAG."""
    sdir = Path(snapshot_dir)
    tag_mod.add_tag(sdir, tag, snapshot)
    click.echo(f"Tagged '{snapshot}' as '{tag}'.")


@tag_group.command(name="remove")
@click.argument("tag")
@click.option("--dir", "snapshot_dir", default=str(DEFAULT_SNAPSHOT_DIR), show_default=True)
def remove_cmd(tag: str, snapshot_dir: str) -> None:
    """Remove TAG."""
    sdir = Path(snapshot_dir)
    removed = tag_mod.remove_tag(sdir, tag)
    if removed:
        click.echo(f"Removed tag '{tag}'.")
    else:
        click.echo(f"Tag '{tag}' not found.", err=True)
        raise SystemExit(1)


@tag_group.command(name="list")
@click.option("--dir", "snapshot_dir", default=str(DEFAULT_SNAPSHOT_DIR), show_default=True)
def list_cmd(snapshot_dir: str) -> None:
    """List all tags."""
    sdir = Path(snapshot_dir)
    tags = tag_mod.list_tags(sdir)
    if not tags:
        click.echo("No tags defined.")
        return
    for t, name in sorted(tags.items()):
        click.echo(f"{t}  ->  {name}")


@tag_group.command(name="resolve")
@click.argument("tag")
@click.option("--dir", "snapshot_dir", default=str(DEFAULT_SNAPSHOT_DIR), show_default=True)
def resolve_cmd(tag: str, snapshot_dir: str) -> None:
    """Print the snapshot name that TAG points to."""
    sdir = Path(snapshot_dir)
    name = tag_mod.resolve_tag(sdir, tag)
    if name is None:
        click.echo(f"Tag '{tag}' not found.", err=True)
        raise SystemExit(1)
    click.echo(name)
