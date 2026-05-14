"""CLI commands for snapshot reports."""
from __future__ import annotations

import click

from envforge.snapshot_report import build_report, format_report


@click.group("report")
def report_group() -> None:
    """Generate reports about snapshots."""


@report_group.command("show")
@click.argument("names", nargs=-1)
@click.option(
    "--dir",
    "snapshot_dir",
    default=".envforge",
    show_default=True,
    help="Directory that stores snapshots.",
)
def show_cmd(names, snapshot_dir: str) -> None:
    """Show a report for one or more snapshots (default: all)."""
    report = build_report(snapshot_dir, list(names) if names else None)
    if report.total_snapshots == 0:
        click.echo("No snapshots found.")
        return
    click.echo(format_report(report))


@report_group.command("summary")
@click.option(
    "--dir",
    "snapshot_dir",
    default=".envforge",
    show_default=True,
    help="Directory that stores snapshots.",
)
def summary_cmd(snapshot_dir: str) -> None:
    """Print a one-line summary of all snapshots."""
    report = build_report(snapshot_dir)
    click.echo(
        f"Snapshots: {report.total_snapshots}  "
        f"With errors: {report.snapshots_with_errors}  "
        f"Expired: {report.expired_count}"
    )
