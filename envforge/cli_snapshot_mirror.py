"""CLI commands for mirroring snapshots between directories."""

from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_mirror import MirrorError, mirror_snapshots


@click.group("mirror")
def mirror_group() -> None:
    """Mirror snapshots between directories."""


@mirror_group.command("run")
@click.argument("source")
@click.argument("destination")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing snapshots in the destination.",
)
@click.option(
    "--name",
    "names",
    multiple=True,
    help="Snapshot name(s) to mirror (may be repeated). Mirrors all if omitted.",
)
def run_cmd(source: str, destination: str, overwrite: bool, names: tuple[str, ...]) -> None:
    """Mirror snapshots from SOURCE directory to DESTINATION directory."""
    src = Path(source)
    dst = Path(destination)

    try:
        result = mirror_snapshots(
            src,
            dst,
            overwrite=overwrite,
            names=list(names) if names else None,
        )
    except MirrorError as exc:
        raise click.ClickException(str(exc)) from exc

    if result.copied:
        click.echo(f"Copied ({len(result.copied)}): {', '.join(result.copied)}")
    if result.overwritten:
        click.echo(f"Overwritten ({len(result.overwritten)}): {', '.join(result.overwritten)}")
    if result.skipped:
        click.echo(f"Skipped ({len(result.skipped)}): {', '.join(result.skipped)}")

    total = result.total_copied + len(result.overwritten)
    click.echo(f"Done. {total} snapshot(s) mirrored to {dst}.")
