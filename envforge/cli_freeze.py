"""CLI commands for freeze/unfreeze of snapshots."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from envforge.snapshot_freeze import (
    freeze_snapshot,
    unfreeze_snapshot,
    is_frozen,
    list_frozen,
)

DEFAULT_DIR = Path(".envforge")


@click.group(name="freeze")
def freeze_group() -> None:
    """Freeze or unfreeze snapshots."""


@freeze_group.command(name="set")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def set_cmd(name: str, snap_dir: str) -> None:
    """Freeze a snapshot to prevent modification."""
    result = freeze_snapshot(Path(snap_dir), name)
    if result.frozen:
        click.echo(f"Frozen: {name}")
    else:
        click.echo(f"Already frozen: {name}")


@freeze_group.command(name="unset")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def unset_cmd(name: str, snap_dir: str) -> None:
    """Unfreeze a snapshot."""
    removed = unfreeze_snapshot(Path(snap_dir), name)
    if removed:
        click.echo(f"Unfrozen: {name}")
    else:
        click.echo(f"Not frozen: {name}")


@freeze_group.command(name="check")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def check_cmd(name: str, snap_dir: str) -> None:
    """Check whether a snapshot is frozen."""
    if is_frozen(Path(snap_dir), name):
        click.echo(f"{name} is frozen")
    else:
        click.echo(f"{name} is not frozen")
        sys.exit(1)


@freeze_group.command(name="list")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def list_cmd(snap_dir: str) -> None:
    """List all frozen snapshots."""
    names = list_frozen(Path(snap_dir))
    if not names:
        click.echo("No frozen snapshots.")
    else:
        for n in names:
            click.echo(n)
