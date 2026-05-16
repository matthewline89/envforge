"""CLI commands for snapshot diff history."""
import click
from pathlib import Path

from envforge.snapshot_diff_history import record_diff, get_diff_history, clear_diff_history


@click.group(name="diff-history")
def diff_history_group() -> None:
    """Manage diff history between snapshots."""


@diff_history_group.command(name="record")
@click.argument("snapshot_a")
@click.argument("snapshot_b")
@click.option("--note", default=None, help="Optional note for this diff.")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def record_cmd(snapshot_a: str, snapshot_b: str, note: str, snapshot_dir: str) -> None:
    """Record a diff between two snapshots."""
    entry = record_diff(Path(snapshot_dir), snapshot_a, snapshot_b, note=note)
    click.echo(f"Recorded diff #{entry.id}: {snapshot_a} -> {snapshot_b} at {entry.timestamp}")
    click.echo(f"  Added: {len(entry.added)}  Removed: {len(entry.removed)}  Changed: {len(entry.changed)}")


@diff_history_group.command(name="log")
@click.option("--snapshot", default=None, help="Filter by snapshot name.")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def log_cmd(snapshot: str, snapshot_dir: str) -> None:
    """List recorded diffs."""
    history = get_diff_history(Path(snapshot_dir), snapshot_name=snapshot)
    if history.is_empty():
        click.echo("No diff history found.")
        return
    for entry in history.entries:
        note_str = f" [{entry.note}]" if entry.note else ""
        click.echo(
            f"#{entry.id}  {entry.snapshot_a} -> {entry.snapshot_b}  "
            f"+{len(entry.added)} -{len(entry.removed)} ~{len(entry.changed)}"
            f"  {entry.timestamp}{note_str}"
        )


@diff_history_group.command(name="clear")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
@click.confirmation_option(prompt="Clear all diff history?")
def clear_cmd(snapshot_dir: str) -> None:
    """Clear all recorded diff history."""
    removed = clear_diff_history(Path(snapshot_dir))
    click.echo(f"Cleared {removed} diff history entries.")
