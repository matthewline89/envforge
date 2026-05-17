"""CLI commands for snapshot revert."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_revert import RevertError, list_revert_points, revert_snapshot

_DEFAULT_DIR = Path.home() / ".envforge" / "snapshots"


@click.group("revert")
def revert_group() -> None:
    """Revert snapshots to previous states."""


@revert_group.command("list")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def list_cmd(name: str, snap_dir: str) -> None:
    """List available revert points for NAME."""
    points = list_revert_points(name, Path(snap_dir))
    if not points:
        click.echo(f"No revert points found for '{name}'.")
        return
    for i, p in enumerate(points):
        ts = p.get("timestamp", "unknown")
        key_count = len(p.get("vars", {}))
        note = p.get("note", "")
        note_str = f"  # {note}" if note else ""
        click.echo(f"[{i}] {ts}  ({key_count} keys){note_str}")


@revert_group.command("run")
@click.argument("name")
@click.option("--index", default=0, show_default=True, help="History entry index (0 = most recent).")
@click.option("--timestamp", default=None, help="Exact ISO timestamp to revert to.")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def run_cmd(name: str, index: int, timestamp: str | None, snap_dir: str) -> None:
    """Revert snapshot NAME to a previous state."""
    try:
        result = revert_snapshot(
            name,
            Path(snap_dir),
            index=index,
            timestamp=timestamp,
        )
    except RevertError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(f"Reverted '{result.name}' to state from {result.reverted_to}.")
    click.echo(f"Keys changed: {result.total_changed}")
    if result.keys_changed:
        for k in result.keys_changed:
            click.echo(f"  ~ {k}")
