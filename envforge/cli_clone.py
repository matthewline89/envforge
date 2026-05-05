"""CLI commands for the *clone* feature."""

from __future__ import annotations

from pathlib import Path

import click

from envforge.clone import CloneError, clone_snapshot


@click.group("clone")
def clone_group() -> None:
    """Clone a snapshot under a new name."""


@clone_group.command("run")
@click.argument("source")
@click.argument("dest")
@click.option(
    "--dir",
    "snapshot_dir",
    default=".envforge",
    show_default=True,
    help="Directory that stores snapshots.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Replace destination snapshot if it already exists.",
)
@click.option(
    "--note",
    default=None,
    help="Optional note to embed in the cloned snapshot.",
)
def run_cmd(
    source: str,
    dest: str,
    snapshot_dir: str,
    overwrite: bool,
    note: str | None,
) -> None:
    """Clone SOURCE snapshot into DEST."""
    directory = Path(snapshot_dir)
    try:
        out = clone_snapshot(
            source=source,
            dest=dest,
            snapshot_dir=directory,
            overwrite=overwrite,
            note=note,
        )
        click.echo(f"Cloned '{source}' → '{dest}' ({out})")
    except CloneError as exc:
        raise click.ClickException(str(exc)) from exc
