"""CLI commands for sorting snapshots."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_sort import sort_snapshots, SortKey


@click.group("sort")
def sort_group() -> None:
    """Sort and list snapshots by various criteria."""


@sort_group.command("run")
@click.option(
    "--by",
    "sort_key",
    type=click.Choice(["name", "size", "keys", "mtime"]),
    default="name",
    show_default=True,
    help="Field to sort by.",
)
@click.option(
    "--desc",
    "descending",
    is_flag=True,
    default=False,
    help="Sort in descending order.",
)
@click.option(
    "--dir",
    "snapshot_dir",
    default=".envforge",
    show_default=True,
    help="Snapshot directory.",
)
def run_cmd(sort_key: str, descending: bool, snapshot_dir: str) -> None:
    """List snapshots sorted by a chosen field."""
    d = Path(snapshot_dir)
    if not d.exists():
        click.echo("No snapshots found.")
        return

    result = sort_snapshots(d, sort_key=sort_key, ascending=not descending)  # type: ignore[arg-type]

    if not result.items:
        click.echo("No snapshots found.")
        return

    order_label = "desc" if descending else "asc"
    click.echo(f"Snapshots sorted by '{sort_key}' ({order_label}):")
    click.echo(f"  {'NAME':<30} {'KEYS':>6} {'SIZE':>10} {'MTIME':>14}")
    click.echo("  " + "-" * 64)
    for item in result.items:
        click.echo(
            f"  {item.name:<30} {item.key_count:>6} {item.size_bytes:>9}B {item.mtime:>14.0f}"
        )
