"""CLI commands for merging snapshots."""

from __future__ import annotations

import click

from envforge.merge import merge_snapshots, save_merge
from envforge.snapshot import get_snapshot_dir


@click.group(name="merge")
def merge_group() -> None:
    """Merge two or more snapshots into one."""


@merge_group.command(name="run")
@click.argument("snapshots", nargs=-1, required=True, metavar="SNAPSHOT...")
@click.option("-o", "--output", required=True, help="Name for the merged snapshot.")
@click.option(
    "--strategy",
    type=click.Choice(["last-wins", "first-wins"], case_sensitive=False),
    default="last-wins",
    show_default=True,
    help="Conflict resolution strategy.",
)
@click.option("--dir", "snapshot_dir", default=None, help="Custom snapshot directory.")
def run_cmd(
    snapshots: tuple[str, ...],
    output: str,
    strategy: str,
    snapshot_dir: str | None,
) -> None:
    """Merge SNAPSHOT... into a new snapshot named OUTPUT."""
    directory = snapshot_dir or get_snapshot_dir()

    if len(snapshots) < 2:
        raise click.UsageError("Provide at least two snapshot names to merge.")

    # Detect duplicate snapshot names early to avoid confusing merge results.
    if len(set(snapshots)) != len(snapshots):
        raise click.UsageError("Duplicate snapshot names are not allowed.")

    try:
        result = merge_snapshots(list(snapshots), directory, strategy=strategy)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    if result.conflicts:
        click.echo(click.style("Conflicts resolved:", fg="yellow"))
        for key, (old, new) in result.conflicts.items():
            click.echo(f"  {key}: '{old}' -> '{new}'")

    path = save_merge(result, output, directory)
    click.echo(
        click.style(f"Merged {len(snapshots)} snapshots into '{output}'.", fg="green")
    )
    click.echo(f"Saved to: {path}")
    click.echo(f"Total variables: {len(result.merged)}")
