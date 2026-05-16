"""CLI commands for the snapshot spotlight feature."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_spotlight import compute_spotlight


@click.group("spotlight")
def spotlight_group() -> None:
    """Surface the most notable snapshots."""


@spotlight_group.command("show")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
@click.option("--top", "top_n", default=5, show_default=True, help="Number of entries to display.")
def show_cmd(snapshot_dir: str, top_n: int) -> None:
    """Show the top-ranked snapshots."""
    path = Path(snapshot_dir)
    report = compute_spotlight(path)

    if report.is_empty():
        click.echo("No snapshots found.")
        return

    entries = report.top(top_n)
    click.echo(f"{'Rank':<5} {'Name':<30} {'Score':>7} {'Rating':>7} {'Accesses':>9} {'Keys':>6}")
    click.echo("-" * 65)
    for rank, entry in enumerate(entries, start=1):
        click.echo(
            f"{rank:<5} {entry.name:<30} {entry.score:>7.1f} {entry.rating:>7} {entry.access_count:>9} {entry.key_count:>6}"
        )


@spotlight_group.command("top")
@click.argument("n", default=3)
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def top_cmd(n: int, snapshot_dir: str) -> None:
    """Print only the names of the top N snapshots."""
    path = Path(snapshot_dir)
    report = compute_spotlight(path)

    if report.is_empty():
        click.echo("No snapshots found.")
        return

    for entry in report.top(n):
        click.echo(entry.name)
