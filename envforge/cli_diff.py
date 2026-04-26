"""CLI commands for diffing environment snapshots."""

from __future__ import annotations

import click

from envforge.diff import diff_snapshots


@click.group(name="diff")
def diff_group() -> None:
    """Compare environment snapshots."""


@diff_group.command(name="run")
@click.argument("snapshot_a")
@click.argument("snapshot_b")
@click.option(
    "--ignore",
    "-i",
    multiple=True,
    metavar="KEY",
    help="Env var key(s) to exclude from the diff. Repeatable.",
)
@click.option(
    "--snapshot-dir",
    default=None,
    envvar="ENVFORGE_SNAPSHOT_DIR",
    help="Directory where snapshots are stored.",
)
@click.option(
    "--exit-code",
    is_flag=True,
    default=False,
    help="Exit with code 1 when differences are found.",
)
def run_cmd(
    snapshot_a: str,
    snapshot_b: str,
    ignore: tuple,
    snapshot_dir: str | None,
    exit_code: bool,
) -> None:
    """Show differences between SNAPSHOT_A and SNAPSHOT_B."""
    try:
        result = diff_snapshots(
            snapshot_a,
            snapshot_b,
            snapshot_dir=snapshot_dir,
            ignore_keys=list(ignore),
        )
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    if result.is_empty:
        click.echo("Snapshots are identical.")
    else:
        added = len(result.added)
        removed = len(result.removed)
        changed = len(result.changed)
        click.echo(
            f"Diff '{snapshot_a}' -> '{snapshot_b}': "
            f"+{added} -{removed} ~{changed}\n"
        )
        click.echo(result.summary())

    if exit_code and not result.is_empty:
        raise SystemExit(1)
