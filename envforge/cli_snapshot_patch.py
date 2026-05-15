"""CLI commands for patching snapshots."""

from __future__ import annotations

import click

from envforge.snapshot_patch import PatchError, patch_snapshot


@click.group(name="patch")
def patch_group() -> None:
    """Partially update a snapshot's environment variables."""


@patch_group.command(name="apply")
@click.argument("name")
@click.option(
    "-s",
    "--set",
    "set_vars",
    multiple=True,
    metavar="KEY=VALUE",
    help="Set a key to a value (can be repeated).",
)
@click.option(
    "-d",
    "--delete",
    "delete_keys",
    multiple=True,
    metavar="KEY",
    help="Delete a key (can be repeated).",
)
@click.option(
    "--dir",
    "snapshot_dir",
    default=".envforge",
    show_default=True,
    help="Snapshot storage directory.",
)
def apply_cmd(
    name: str,
    set_vars: tuple,
    delete_keys: tuple,
    snapshot_dir: str,
) -> None:
    """Apply a patch to snapshot NAME."""
    parsed: dict[str, str] = {}
    for item in set_vars:
        if "=" not in item:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {item!r}")
        k, v = item.split("=", 1)
        parsed[k] = v

    try:
        result = patch_snapshot(
            name,
            snapshot_dir,
            set_vars=parsed,
            delete_keys=list(delete_keys),
        )
    except PatchError as exc:
        raise click.ClickException(str(exc))

    click.echo(f"Patched snapshot '{name}'")
    if result.added:
        click.echo(f"  Added:   {', '.join(result.added)}")
    if result.updated:
        click.echo(f"  Updated: {', '.join(result.updated)}")
    if result.deleted:
        click.echo(f"  Deleted: {', '.join(result.deleted)}")
    if result.total_changes == 0:
        click.echo("  No changes applied.")
