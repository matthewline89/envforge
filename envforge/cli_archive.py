"""CLI commands for snapshot archiving."""

from __future__ import annotations

from pathlib import Path

import click

from envforge.archive import ArchiveError, create_archive, extract_archive, list_archive


@click.group("archive")
def archive_group() -> None:
    """Bundle and restore snapshot archives."""


@archive_group.command("create")
@click.argument("archive_path", type=click.Path())
@click.option("--snapshot-dir", default=".envforge", show_default=True, help="Snapshot storage directory.")
@click.option("--name", "names", multiple=True, help="Snapshot name(s) to include (default: all).")
def create_cmd(archive_path: str, snapshot_dir: str, names: tuple[str, ...]) -> None:
    """Create a zip archive from snapshots."""
    try:
        result = create_archive(
            snapshot_dir=Path(snapshot_dir),
            archive_path=Path(archive_path),
            names=list(names) if names else None,
        )
        click.echo(f"Archived {result.count} snapshot(s) to {result.path}")
        for name in result.snapshots:
            click.echo(f"  + {name}")
    except ArchiveError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@archive_group.command("extract")
@click.argument("archive_path", type=click.Path(exists=True))
@click.option("--snapshot-dir", default=".envforge", show_default=True, help="Destination snapshot directory.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing snapshots.")
def extract_cmd(archive_path: str, snapshot_dir: str, overwrite: bool) -> None:
    """Extract snapshots from a zip archive."""
    try:
        result = extract_archive(
            archive_path=Path(archive_path),
            snapshot_dir=Path(snapshot_dir),
            overwrite=overwrite,
        )
        click.echo(f"Extracted {result.count} snapshot(s) from {result.path}")
        for name in result.snapshots:
            click.echo(f"  + {name}")
    except ArchiveError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@archive_group.command("list")
@click.argument("archive_path", type=click.Path(exists=True))
def list_cmd(archive_path: str) -> None:
    """List snapshots contained in an archive."""
    try:
        names = list_archive(Path(archive_path))
        if not names:
            click.echo("Archive is empty.")
        else:
            click.echo(f"{len(names)} snapshot(s) in archive:")
            for name in names:
                click.echo(f"  {name}")
    except ArchiveError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
