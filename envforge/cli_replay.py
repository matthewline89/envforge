"""CLI commands for the replay feature."""

from __future__ import annotations

import click

from envforge.replay import ReplayError, replay_snapshot


@click.group("replay")
def replay_group() -> None:
    """Replay and transform snapshots."""


@replay_group.command("run")
@click.argument("source")
@click.argument("destination")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
@click.option("--prefix", default=None, help="Only include keys with this prefix.")
@click.option(
    "--upper-keys",
    is_flag=True,
    default=False,
    help="Transform all keys to uppercase.",
)
@click.option(
    "--exclude",
    multiple=True,
    metavar="KEY",
    help="Keys to exclude (repeatable).",
)
def run_cmd(
    source: str,
    destination: str,
    snapshot_dir: str,
    prefix: str | None,
    upper_keys: bool,
    exclude: tuple[str, ...],
) -> None:
    """Replay SOURCE snapshot into DESTINATION with optional transforms."""
    key_transform = (lambda k: k.upper()) if upper_keys else None
    try:
        result = replay_snapshot(
            source,
            destination,
            snapshot_dir,
            prefix_filter=prefix,
            key_transform=key_transform,
            exclude_keys=list(exclude),
        )
    except ReplayError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Replayed '{result.source}' → '{result.destination}'")
    click.echo(f"  Keys included : {len(result.env)}")
    click.echo(f"  Keys skipped  : {len(result.skipped_keys)}")
    click.echo(f"  Transforms    : {len(result.applied_transforms)}")
    if result.skipped_keys:
        click.echo("  Skipped: " + ", ".join(result.skipped_keys))
