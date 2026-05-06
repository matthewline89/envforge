"""CLI commands for snapshot annotations."""

from __future__ import annotations

from pathlib import Path

import click

from envforge.annotate import (
    get_annotation,
    list_annotations,
    remove_annotation,
    set_annotation,
)

_DEFAULT_DIR = Path.home() / ".envforge" / "snapshots"


@click.group("annotate")
def annotate_group() -> None:
    """Attach notes to snapshots."""


@annotate_group.command("set")
@click.argument("name")
@click.argument("note")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def set_cmd(name: str, note: str, snap_dir: str) -> None:
    """Attach NOTE to snapshot NAME."""
    set_annotation(Path(snap_dir), name, note)
    click.echo(f"Annotation set for '{name}'.")


@annotate_group.command("remove")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def remove_cmd(name: str, snap_dir: str) -> None:
    """Remove the annotation for snapshot NAME."""
    removed = remove_annotation(Path(snap_dir), name)
    if removed:
        click.echo(f"Annotation removed for '{name}'.")
    else:
        click.echo(f"No annotation found for '{name}'.")


@annotate_group.command("show")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def show_cmd(name: str, snap_dir: str) -> None:
    """Show the annotation for snapshot NAME."""
    note = get_annotation(Path(snap_dir), name)
    if note is None:
        click.echo(f"No annotation for '{name}'.")
    else:
        click.echo(note)


@annotate_group.command("list")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def list_cmd(snap_dir: str) -> None:
    """List all annotated snapshots."""
    annotations = list_annotations(Path(snap_dir))
    if not annotations:
        click.echo("No annotations found.")
        return
    for name, note in sorted(annotations.items()):
        click.echo(f"{name}: {note}")
