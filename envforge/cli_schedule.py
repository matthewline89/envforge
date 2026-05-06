"""CLI commands for scheduled snapshots."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.schedule import start_schedule


@click.group("schedule")
def schedule_group() -> None:
    """Manage scheduled automatic snapshots."""


@schedule_group.command("run")
@click.argument("name")
@click.option(
    "--interval",
    default=60,
    show_default=True,
    help="Seconds between snapshots.",
)
@click.option(
    "--runs",
    default=1,
    show_default=True,
    help="Number of snapshots to take (1 = run once).",
)
@click.option(
    "--dir",
    "snapshot_dir",
    default=".envforge",
    show_default=True,
    help="Directory to store snapshots.",
)
def run_cmd(
    name: str,
    interval: int,
    runs: int,
    snapshot_dir: str,
) -> None:
    """Take NAME snapshots on a fixed INTERVAL."""
    snap_dir = Path(snapshot_dir)
    snap_dir.mkdir(parents=True, exist_ok=True)

    def _on_snapshot(saved_name: str) -> None:
        click.echo(f"Snapshot saved: {saved_name}")

    session = start_schedule(
        snapshot_dir=snap_dir,
        snapshot_name=name,
        interval_seconds=interval,
        max_runs=runs,
        on_snapshot=_on_snapshot,
    )
    click.echo(
        f"Schedule complete. {session.entries[0].run_count} snapshot(s) taken."
    )
