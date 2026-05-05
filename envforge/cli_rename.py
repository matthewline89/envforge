"""CLI commands for renaming snapshots."""

from __future__ import annotations

from pathlib import Path

import click

from envforge.rename import RenameError, rename_snapshot


@click.group(name="rename")
def rename_group() -> None:
    """Rename a snapshot."""


@rename_group.command(name="run")
@click.argument("old_name")
@click.argument("new_name")
@click.option(
    "--dir",
    "snapshot_dir",
    default=".envforge/snapshots",
    show_default=True,
    help="Directory where snapshots are stored.",
)
@click.option(
    "--no-migrate-tags",
    is_flag=True,
    default=False,
    help="Skip migrating tags that reference the old name.",
)
@click.option(
    "--no-migrate-aliases",
    is_flag=True,
    default=False,
    help="Skip migrating aliases that reference the old name.",
)
def run_cmd(
    old_name: str,
    new_name: str,
    snapshot_dir: str,
    no_migrate_tags: bool,
    no_migrate_aliases: bool,
) -> None:
    """Rename OLD_NAME snapshot to NEW_NAME."""
    directory = Path(snapshot_dir)
    try:
        dest = rename_snapshot(
            directory,
            old_name,
            new_name,
            migrate_tags=not no_migrate_tags,
            migrate_aliases=not no_migrate_aliases,
        )
        click.echo(f"Renamed '{old_name}' → '{new_name}' ({dest})")
    except RenameError as exc:
        raise click.ClickException(str(exc)) from exc
