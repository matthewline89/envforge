"""CLI commands for the watch feature."""

from __future__ import annotations

import click
from pathlib import Path

from envforge.watch import start_watch, session_summary, WatchEvent


@click.group("watch")
def watch_group() -> None:
    """Watch environment variables for changes."""


@watch_group.command("start")
@click.option(
    "--dir",
    "snapshot_dir",
    default=".envforge",
    show_default=True,
    help="Directory to store snapshots.",
)
@click.option(
    "--interval",
    default=5.0,
    show_default=True,
    type=float,
    help="Poll interval in seconds.",
)
@click.option(
    "--count",
    default=0,
    show_default=True,
    type=int,
    help="Number of polls before stopping (0 = run forever).",
)
def start_cmd(snapshot_dir: str, interval: float, count: int) -> None:
    """Start watching environment variables for changes."""
    snap_path = Path(snapshot_dir)
    snap_path.mkdir(parents=True, exist_ok=True)

    def _on_change(event: WatchEvent) -> None:
        click.echo(f"[change] {event.snapshot_name}: {event.diff.summary()}")

    click.echo(f"Watching environment every {interval}s. Press Ctrl+C to stop.")
    try:
        session = start_watch(
            snapshot_dir=snap_path,
            interval=interval,
            iterations=count,
            on_change=_on_change,
        )
    except KeyboardInterrupt:
        click.echo("\nWatch stopped.")
        return

    click.echo(session_summary(session))
