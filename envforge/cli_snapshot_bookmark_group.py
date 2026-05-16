"""CLI commands for the bookmark-group cross-reference feature."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_bookmark_group import build_report


@click.group("bookmark-group")
def bookmark_group_group() -> None:
    """Cross-reference bookmarks with groups."""


@bookmark_group_group.command("report")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def report_cmd(snap_dir: str) -> None:
    """Show all bookmarks alongside their groups."""
    report = build_report(Path(snap_dir))
    if report.is_empty():
        click.echo("No bookmarks found.")
        return
    for entry in report.entries:
        groups_str = ", ".join(entry.groups) if entry.groups else "(none)"
        click.echo(f"{entry.bookmark} -> {entry.snapshot}  groups: {groups_str}")


@bookmark_group_group.command("find")
@click.argument("group")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def find_cmd(group: str, snap_dir: str) -> None:
    """List bookmarks whose snapshot belongs to GROUP."""
    report = build_report(Path(snap_dir))
    matches = report.bookmarks_in_group(group)
    if not matches:
        click.echo(f"No bookmarks found in group '{group}'.")
        return
    for bm in matches:
        click.echo(bm)


@bookmark_group_group.command("show")
@click.argument("bookmark")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def show_cmd(bookmark: str, snap_dir: str) -> None:
    """Show groups for a specific BOOKMARK."""
    report = build_report(Path(snap_dir))
    entry = report.for_bookmark(bookmark)
    if entry is None:
        click.echo(f"Bookmark '{bookmark}' not found.")
        return
    click.echo(f"snapshot: {entry.snapshot}")
    if entry.groups:
        for g in entry.groups:
            click.echo(f"  group: {g}")
    else:
        click.echo("  (no groups)")
