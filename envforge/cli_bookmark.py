"""CLI commands for bookmark management."""

from __future__ import annotations

from pathlib import Path

import click

from envforge.bookmark import (
    list_bookmarks,
    remove_bookmark,
    resolve_bookmark,
    set_bookmark,
)

_DEFAULT_DIR = Path.home() / ".envforge"


@click.group("bookmark")
def bookmark_group() -> None:
    """Manage snapshot bookmarks."""


@bookmark_group.command("set")
@click.argument("bookmark")
@click.argument("snapshot_name")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def set_cmd(bookmark: str, snapshot_name: str, snap_dir: str) -> None:
    """Assign BOOKMARK to SNAPSHOT_NAME."""
    directory = Path(snap_dir)
    directory.mkdir(parents=True, exist_ok=True)
    is_new = set_bookmark(directory, bookmark, snapshot_name)
    if is_new:
        click.echo(f"Bookmark '{bookmark}' -> '{snapshot_name}' created.")
    else:
        click.echo(f"Bookmark '{bookmark}' updated to '{snapshot_name}'.")


@bookmark_group.command("remove")
@click.argument("bookmark")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def remove_cmd(bookmark: str, snap_dir: str) -> None:
    """Remove a bookmark."""
    found = remove_bookmark(Path(snap_dir), bookmark)
    if found:
        click.echo(f"Bookmark '{bookmark}' removed.")
    else:
        click.echo(f"Bookmark '{bookmark}' not found.", err=True)


@bookmark_group.command("list")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def list_cmd(snap_dir: str) -> None:
    """List all bookmarks."""
    bookmarks = list_bookmarks(Path(snap_dir))
    if not bookmarks:
        click.echo("No bookmarks defined.")
        return
    for bm, name in sorted(bookmarks.items()):
        click.echo(f"{bm} -> {name}")


@bookmark_group.command("resolve")
@click.argument("bookmark")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def resolve_cmd(bookmark: str, snap_dir: str) -> None:
    """Print the snapshot name for a bookmark."""
    name = resolve_bookmark(Path(snap_dir), bookmark)
    if name is None:
        click.echo(f"Bookmark '{bookmark}' not found.", err=True)
    else:
        click.echo(name)
