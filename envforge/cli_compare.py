"""CLI commands for comparing multiple snapshots side-by-side."""

from __future__ import annotations

import click

from envforge.compare import compare_snapshots
from envforge.snapshot import DEFAULT_SNAPSHOT_DIR


@click.group("compare")
def compare_group() -> None:
    """Compare multiple snapshots side-by-side."""


@compare_group.command("run")
@click.argument("snapshots", nargs=-1, required=True)
@click.option(
    "--snapshot-dir",
    default=None,
    help="Directory where snapshots are stored.",
    type=click.Path(),
)
@click.option(
    "--only-diff",
    is_flag=True,
    default=False,
    help="Show only keys that differ across snapshots.",
)
def run_cmd(snapshots: tuple, snapshot_dir: str, only_diff: bool) -> None:
    """Compare SNAPSHOTS side-by-side."""
    if len(snapshots) < 2:
        raise click.UsageError("Provide at least two snapshot names.")

    directory = snapshot_dir or DEFAULT_SNAPSHOT_DIR

    try:
        report = compare_snapshots(list(snapshots), snapshot_dir=directory)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    keys_to_show = report.differing_keys() if only_diff else report.all_keys()
    if not keys_to_show:
        click.echo("No differences found.")
        return

    # Header
    col_w = 28
    header = f"{'KEY':<30}" + "".join(f"{n:<{col_w}}" for n in report.snapshot_names)
    click.echo(header)
    click.echo("-" * len(header))

    for key in sorted(keys_to_show):
        row = f"{key:<30}"
        for name in report.snapshot_names:
            val = report.matrix[key].get(name)
            display = val if val is not None else "<missing>"
            row += f"{display:<{col_w}}"
        click.echo(row)

    # Summary footer
    click.echo()
    click.echo(
        f"Common keys: {len(report.common_keys())}  "
        f"Differing: {len(report.differing_keys())}  "
        f"Total: {len(report.all_keys())}"
    )
