"""CLI commands for filtering snapshots."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_filter import (
    filter_by_key,
    filter_by_value,
    filter_by_size,
)

DEFAULT_DIR = Path.home() / ".envforge" / "snapshots"


@click.group(name="filter")
def filter_group() -> None:
    """Filter snapshots by key, value, or size criteria."""


@filter_group.command(name="by-key")
@click.argument("pattern")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def by_key_cmd(pattern: str, snap_dir: str) -> None:
    """List snapshots containing a key matching PATTERN (glob)."""
    result = filter_by_key(Path(snap_dir), pattern)
    if result.is_empty():
        click.echo(f"No snapshots matched key pattern '{pattern}'.")
    else:
        click.echo(f"Matched {len(result)}/{result.total_scanned} snapshot(s):")
        for name in result.matched:
            click.echo(f"  {name}")


@filter_group.command(name="by-value")
@click.argument("pattern")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def by_value_cmd(pattern: str, snap_dir: str) -> None:
    """List snapshots containing a value matching PATTERN (glob)."""
    result = filter_by_value(Path(snap_dir), pattern)
    if result.is_empty():
        click.echo(f"No snapshots matched value pattern '{pattern}'.")
    else:
        click.echo(f"Matched {len(result)}/{result.total_scanned} snapshot(s):")
        for name in result.matched:
            click.echo(f"  {name}")


@filter_group.command(name="by-size")
@click.option("--min", "min_keys", default=0, show_default=True, type=int)
@click.option("--max", "max_keys", default=None, type=int)
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def by_size_cmd(min_keys: int, max_keys: int | None, snap_dir: str) -> None:
    """List snapshots whose key count is within [--min, --max]."""
    result = filter_by_size(Path(snap_dir), min_keys=min_keys, max_keys=max_keys)
    if result.is_empty():
        click.echo("No snapshots matched the size criteria.")
    else:
        click.echo(f"Matched {len(result)}/{result.total_scanned} snapshot(s):")
        for name in result.matched:
            click.echo(f"  {name}")
