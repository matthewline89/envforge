"""CLI commands for snapshot streak tracking."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_streak import compute_streak, record_activity

DEFAULT_DIR = Path(".envforge")


@click.group("streak")
def streak_group() -> None:
    """Track consecutive daily snapshot activity streaks."""


@streak_group.command("record")
@click.argument("snapshot")
@click.option("--date", "on_date", default=None, help="ISO date (YYYY-MM-DD); defaults to today.")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def record_cmd(snapshot: str, on_date: str | None, snap_dir: str) -> None:
    """Record activity for SNAPSHOT on a given date."""
    d = Path(snap_dir)
    d.mkdir(parents=True, exist_ok=True)
    entry = record_activity(d, snapshot, on_date)
    click.echo(f"Recorded activity for '{snapshot}' on {entry.date}.")


@streak_group.command("show")
@click.argument("snapshot")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def show_cmd(snapshot: str, snap_dir: str) -> None:
    """Show streak report for SNAPSHOT."""
    report = compute_streak(Path(snap_dir), snapshot)
    if report.is_empty():
        click.echo(f"No activity recorded for '{snapshot}'.")
        return
    click.echo(f"Snapshot : {report.snapshot}")
    click.echo(f"Days active  : {len(report.dates)}")
    click.echo(f"Current streak : {report.current_streak} day(s)")
    click.echo(f"Longest streak : {report.longest_streak} day(s)")
