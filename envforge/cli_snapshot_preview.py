"""CLI commands for snapshot preview."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_preview import format_preview, preview_snapshot

_DEFAULT_DIR = Path.home() / ".envforge" / "snapshots"


@click.group("preview")
def preview_group() -> None:
    """Preview snapshot contents."""


@preview_group.command("show")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
@click.option("--no-mask", is_flag=True, default=False, help="Show secret values in plain text.")
@click.option("--limit", default=None, type=int, help="Maximum number of keys to display.")
@click.option("--filter", "key_filter", default=None, help="Only show keys containing this string.")
@click.option("--index", is_flag=True, default=False, help="Show line numbers.")
def show_cmd(
    name: str,
    snap_dir: str,
    no_mask: bool,
    limit: int | None,
    key_filter: str | None,
    index: bool,
) -> None:
    """Display a formatted preview of a snapshot."""
    directory = Path(snap_dir)
    try:
        preview = preview_snapshot(
            name,
            directory,
            mask_secrets=not no_mask,
            limit=limit,
            key_filter=key_filter,
        )
    except FileNotFoundError:
        click.echo(f"Snapshot '{name}' not found.", err=True)
        raise SystemExit(1)

    if not preview.lines:
        click.echo("No matching keys to display.")
        return

    click.echo(f"Preview: {preview.name}  ({len(preview)} key(s))")
    click.echo("-" * 40)
    click.echo(format_preview(preview, show_index=index))
    if preview.truncated:
        click.echo(f"(use --limit to adjust the number of rows shown)")
