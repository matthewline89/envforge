"""CLI commands for the label feature."""
from __future__ import annotations

from pathlib import Path

import click

from envforge import label as _label


@click.group("label")
def label_group() -> None:
    """Attach and query freeform labels on snapshots."""


@label_group.command("add")
@click.argument("snapshot_name")
@click.argument("label_value")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def add_cmd(snapshot_name: str, label_value: str, snap_dir: str) -> None:
    """Add LABEL_VALUE to SNAPSHOT_NAME."""
    d = Path(snap_dir)
    is_new = _label.add_label(d, snapshot_name, label_value)
    if is_new:
        click.echo(f"Label '{label_value}' added to '{snapshot_name}'.")
    else:
        click.echo(f"Label '{label_value}' already exists on '{snapshot_name}'.")


@label_group.command("remove")
@click.argument("snapshot_name")
@click.argument("label_value")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def remove_cmd(snapshot_name: str, label_value: str, snap_dir: str) -> None:
    """Remove LABEL_VALUE from SNAPSHOT_NAME."""
    d = Path(snap_dir)
    removed = _label.remove_label(d, snapshot_name, label_value)
    if removed:
        click.echo(f"Label '{label_value}' removed from '{snapshot_name}'.")
    else:
        click.echo(f"Label '{label_value}' not found on '{snapshot_name}'.")


@label_group.command("show")
@click.argument("snapshot_name")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def show_cmd(snapshot_name: str, snap_dir: str) -> None:
    """Show all labels on SNAPSHOT_NAME."""
    labels = _label.get_labels(Path(snap_dir), snapshot_name)
    if not labels:
        click.echo(f"No labels on '{snapshot_name}'.")
    else:
        for lbl in labels:
            click.echo(lbl)


@label_group.command("find")
@click.argument("label_value")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def find_cmd(label_value: str, snap_dir: str) -> None:
    """List snapshots that carry LABEL_VALUE."""
    names = _label.find_by_label(Path(snap_dir), label_value)
    if not names:
        click.echo(f"No snapshots found with label '{label_value}'.")
    else:
        for name in names:
            click.echo(name)


@label_group.command("list")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def list_cmd(snap_dir: str) -> None:
    """List all snapshot→label mappings."""
    data = _label.list_labels(Path(snap_dir))
    if not data:
        click.echo("No labels defined.")
    else:
        for name, labels in data.items():
            click.echo(f"{name}: {', '.join(labels)}")
