"""CLI commands for locking and unlocking snapshots."""

from __future__ import annotations

from pathlib import Path

import click

from envforge import lock as lock_mod

_DEFAULT_DIR = Path.home() / ".envforge"


@click.group("lock")
def lock_group() -> None:
    """Lock or unlock snapshots to prevent modification."""


@lock_group.command("set")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=str(_DEFAULT_DIR), show_default=True)
def set_cmd(name: str, snapshot_dir: str) -> None:
    """Lock a snapshot by NAME."""
    path = Path(snapshot_dir)
    path.mkdir(parents=True, exist_ok=True)
    newly_locked = lock_mod.lock_snapshot(path, name)
    if newly_locked:
        click.echo(f"Snapshot '{name}' is now locked.")
    else:
        click.echo(f"Snapshot '{name}' was already locked.")


@lock_group.command("unset")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=str(_DEFAULT_DIR), show_default=True)
def unset_cmd(name: str, snapshot_dir: str) -> None:
    """Unlock a snapshot by NAME."""
    path = Path(snapshot_dir)
    removed = lock_mod.unlock_snapshot(path, name)
    if removed:
        click.echo(f"Snapshot '{name}' is now unlocked.")
    else:
        click.echo(f"Snapshot '{name}' was not locked.")


@lock_group.command("list")
@click.option("--dir", "snapshot_dir", default=str(_DEFAULT_DIR), show_default=True)
def list_cmd(snapshot_dir: str) -> None:
    """List all locked snapshots."""
    path = Path(snapshot_dir)
    locks = lock_mod.list_locks(path)
    if not locks:
        click.echo("No snapshots are currently locked.")
    else:
        for name in locks:
            click.echo(name)


@lock_group.command("check")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=str(_DEFAULT_DIR), show_default=True)
def check_cmd(name: str, snapshot_dir: str) -> None:
    """Check whether a snapshot is locked."""
    path = Path(snapshot_dir)
    if lock_mod.is_locked(path, name):
        click.echo(f"Snapshot '{name}' is locked.")
    else:
        click.echo(f"Snapshot '{name}' is not locked.")
