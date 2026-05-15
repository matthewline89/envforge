"""CLI commands for snapshot trend analysis."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_trend import build_trend


@click.group("trend")
def trend_group() -> None:
    """Analyse how a snapshot's key count changes over time."""


@trend_group.command("show")
@click.argument("name")
@click.option(
    "--dir",
    "snapshot_dir",
    default=".envforge",
    show_default=True,
    help="Directory where snapshots are stored.",
)
def show_cmd(name: str, snapshot_dir: str) -> None:
    """Show the key-count trend for a snapshot."""
    report = build_trend(name, Path(snapshot_dir))

    if report.is_empty:
        click.echo(f"No trend data available for '{name}'.")
        return

    click.echo(f"Trend for '{name}' ({len(report.points)} point(s)):")
    click.echo(f"  min keys : {report.min_keys}")
    click.echo(f"  max keys : {report.max_keys}")
    delta_sign = "+" if report.delta >= 0 else ""
    click.echo(f"  delta    : {delta_sign}{report.delta}")
    click.echo("")
    for pt in report.points:
        note = f"  [{pt.note}]" if pt.note else ""
        click.echo(f"  {pt.timestamp}  keys={pt.key_count}{note}")
