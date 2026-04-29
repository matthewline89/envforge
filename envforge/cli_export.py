"""CLI commands for exporting snapshots to various formats."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.export import export_snapshot, export_to_file


@click.group("export")
def export_group() -> None:
    """Export a snapshot to dotenv, JSON, YAML, or shell format."""


@export_group.command("run")
@click.argument("snapshot_name")
@click.option(
    "--format", "fmt",
    type=click.Choice(["dotenv", "json", "yaml", "shell"], case_sensitive=False),
    default="dotenv",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--output", "-o",
    type=click.Path(dir_okay=False, writable=True),
    default=None,
    help="Write output to this file instead of stdout.",
)
@click.option(
    "--dir", "snapshot_dir",
    type=click.Path(file_okay=False),
    default=".envforge",
    show_default=True,
    help="Snapshot storage directory.",
)
def run_cmd(snapshot_name: str, fmt: str, output: str | None, snapshot_dir: str) -> None:
    """Export SNAPSHOT_NAME in the chosen format."""
    sdir = Path(snapshot_dir)
    try:
        if output:
            dest = export_to_file(snapshot_name, fmt, Path(output), sdir)  # type: ignore[arg-type]
            click.echo(f"Exported '{snapshot_name}' ({fmt}) → {dest}")
        else:
            content = export_snapshot(snapshot_name, fmt, sdir)  # type: ignore[arg-type]
            click.echo(content, nl=False)
    except FileNotFoundError:
        click.echo(f"Snapshot '{snapshot_name}' not found.", err=True)
        raise SystemExit(1)
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
