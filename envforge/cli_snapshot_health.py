"""CLI commands for snapshot health checks."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_health import check_health
from envforge.snapshot import list_snapshots

DEFAULT_DIR = Path.home() / ".envforge"


@click.group("health")
def health_group() -> None:
    """Check the health of snapshots."""


@health_group.command("show")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=str(DEFAULT_DIR), show_default=True)
def show_cmd(name: str, snapshot_dir: str) -> None:
    """Show the health report for a single snapshot."""
    report = check_health(name, Path(snapshot_dir))
    click.echo(f"Snapshot : {report.name}")
    click.echo(f"Status   : {report.status}")
    click.echo(f"Locked   : {'yes' if report.locked else 'no'}")
    click.echo(f"Frozen   : {'yes' if report.frozen else 'no'}")
    if report.errors:
        click.echo("Errors:")
        for e in report.errors:
            click.echo(f"  [error] {e}")
    if report.warnings:
        click.echo("Warnings:")
        for w in report.warnings:
            click.echo(f"  [warn]  {w}")
    if report.healthy:
        click.echo("Health   : OK")


@health_group.command("scan")
@click.option("--dir", "snapshot_dir", default=str(DEFAULT_DIR), show_default=True)
@click.option("--errors-only", is_flag=True, default=False)
def scan_cmd(snapshot_dir: str, errors_only: bool) -> None:
    """Scan all snapshots and print a health summary."""
    sd = Path(snapshot_dir)
    names = list_snapshots(sd)
    if not names:
        click.echo("No snapshots found.")
        return
    for name in names:
        report = check_health(name, sd)
        if errors_only and report.healthy:
            continue
        flag = "[OK]     " if report.healthy else f"[{report.status.upper()}]".ljust(9)
        click.echo(f"{flag} {name}")
