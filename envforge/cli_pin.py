"""CLI commands for managing snapshot pins."""
from __future__ import annotations

from pathlib import Path

import click

from envforge import pin as pin_mod


@click.group("pin")
def pin_group() -> None:
    """Pin snapshots to named version slots."""


@pin_group.command("set")
@click.argument("pin_name")
@click.argument("snapshot_name")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def set_cmd(pin_name: str, snapshot_name: str, snap_dir: str) -> None:
    """Pin SNAPSHOT_NAME to PIN_NAME slot."""
    pin_mod.set_pin(Path(snap_dir), pin_name, snapshot_name)
    click.echo(f"Pinned '{pin_name}' → '{snapshot_name}'")


@pin_group.command("remove")
@click.argument("pin_name")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def remove_cmd(pin_name: str, snap_dir: str) -> None:
    """Remove a pin by name."""
    removed = pin_mod.remove_pin(Path(snap_dir), pin_name)
    if removed:
        click.echo(f"Removed pin '{pin_name}'")
    else:
        click.echo(f"Pin '{pin_name}' not found", err=True)
        raise SystemExit(1)


@pin_group.command("list")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def list_cmd(snap_dir: str) -> None:
    """List all pins."""
    pins = pin_mod.list_pins(Path(snap_dir))
    if not pins:
        click.echo("No pins defined.")
        return
    for name, snapshot in sorted(pins.items()):
        click.echo(f"{name}  →  {snapshot}")


@pin_group.command("resolve")
@click.argument("pin_name")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def resolve_cmd(pin_name: str, snap_dir: str) -> None:
    """Print the snapshot name a pin points to."""
    snapshot = pin_mod.resolve_pin(Path(snap_dir), pin_name)
    if snapshot is None:
        click.echo(f"Pin '{pin_name}' not found", err=True)
        raise SystemExit(1)
    click.echo(snapshot)
