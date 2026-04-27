"""CLI commands for searching across snapshots."""

from __future__ import annotations

from pathlib import Path

import click

from envforge.search import search_snapshots

DEFAULT_SNAPSHOT_DIR = Path.home() / ".envforge" / "snapshots"


@click.group(name="search")
def search_group() -> None:
    """Search for keys or values across snapshots."""


@search_group.command(name="run")
@click.argument("pattern")
@click.option("--snapshot", "-s", default=None, help="Limit search to a specific snapshot.")
@click.option("--keys-only", is_flag=True, default=False, help="Search only in keys.")
@click.option("--values-only", is_flag=True, default=False, help="Search only in values.")
@click.option("--case-sensitive", is_flag=True, default=False, help="Enable case-sensitive matching.")
@click.option(
    "--snapshot-dir",
    default=str(DEFAULT_SNAPSHOT_DIR),
    show_default=True,
    help="Directory where snapshots are stored.",
)
def run_cmd(
    pattern: str,
    snapshot: str | None,
    keys_only: bool,
    values_only: bool,
    case_sensitive: bool,
    snapshot_dir: str,
) -> None:
    """Search snapshots for PATTERN (supports regex)."""
    search_keys = not values_only
    search_values = not keys_only

    try:
        result = search_snapshots(
            pattern=pattern,
            snapshot_dir=Path(snapshot_dir),
            search_keys=search_keys,
            search_values=search_values,
            snapshot_name=snapshot,
            case_sensitive=case_sensitive,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc))

    if result.is_empty():
        click.echo("No matches found.")
        return

    grouped = result.grouped_by_snapshot()
    for snap_name, matches in grouped.items():
        click.echo(click.style(f"[{snap_name}]", fg="cyan", bold=True))
        for match in matches:
            click.echo(f"  {click.style(match.key, fg='yellow')} = {match.value}")

    click.echo(f"\nTotal matches: {len(result.matches)}")
