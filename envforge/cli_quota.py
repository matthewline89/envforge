"""CLI commands for snapshot quota management."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_quota import check_quota, get_quota, remove_quota, set_quota

_DEFAULT_DIR = Path.home() / ".envforge"


@click.group("quota")
def quota_group() -> None:
    """Manage snapshot count quotas."""


@quota_group.command("set")
@click.argument("limit", type=int)
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def set_cmd(limit: int, snap_dir: str) -> None:
    """Set the maximum number of snapshots allowed."""
    try:
        set_quota(Path(snap_dir), limit)
        click.echo(f"Quota set to {limit} snapshot(s).")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@quota_group.command("remove")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def remove_cmd(snap_dir: str) -> None:
    """Remove the quota for the snapshot directory."""
    removed = remove_quota(Path(snap_dir))
    if removed:
        click.echo("Quota removed.")
    else:
        click.echo("No quota was set.")


@quota_group.command("check")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def check_cmd(snap_dir: str) -> None:
    """Show current usage against the configured quota."""
    try:
        result = check_quota(Path(snap_dir))
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    status = "EXCEEDED" if result.exceeded else "OK"
    click.echo(f"Limit  : {result.limit}")
    click.echo(f"Current: {result.current}")
    click.echo(f"Status : {status}")
    if not result.exceeded:
        click.echo(f"Headroom: {result.headroom}")
