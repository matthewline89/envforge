"""CLI commands for snapshot chaining."""

from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_chain import (
    ChainError,
    get_chain,
    link_snapshot,
    list_chains,
    unlink_snapshot,
)


@click.group("chain")
def chain_group() -> None:
    """Manage snapshot parent-child chains."""


@chain_group.command("link")
@click.argument("name")
@click.option("--parent", default=None, help="Parent snapshot name (omit for root).")
@click.option(
    "--dir",
    "snapshot_dir",
    default=".envforge",
    show_default=True,
    help="Snapshot directory.",
)
def link_cmd(name: str, parent: str | None, snapshot_dir: str) -> None:
    """Link NAME to PARENT in a chain."""
    d = Path(snapshot_dir)
    d.mkdir(parents=True, exist_ok=True)
    is_new = link_snapshot(d, name, parent)
    if is_new:
        msg = f"Linked '{name}'"
        msg += f" → parent '{parent}'" if parent else " as chain root"
        click.echo(msg)
    else:
        click.echo(f"Updated chain link for '{name}'.")


@chain_group.command("unlink")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def unlink_cmd(name: str, snapshot_dir: str) -> None:
    """Remove NAME from chain records."""
    d = Path(snapshot_dir)
    removed = unlink_snapshot(d, name)
    if removed:
        click.echo(f"Unlinked '{name}' from chain.")
    else:
        click.echo(f"'{name}' was not part of any chain.", err=True)


@chain_group.command("show")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def show_cmd(name: str, snapshot_dir: str) -> None:
    """Show the full chain ending at NAME (root first)."""
    d = Path(snapshot_dir)
    try:
        chain = get_chain(d, name)
    except ChainError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    for i, entry in enumerate(chain.entries):
        prefix = "  " * i + ("└─ " if i else "")
        click.echo(f"{prefix}{entry.name}")


@chain_group.command("list")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def list_cmd(snapshot_dir: str) -> None:
    """List all chained snapshots and their parents."""
    d = Path(snapshot_dir)
    data = list_chains(d)
    if not data:
        click.echo("No chain links recorded.")
        return
    for name, parent in sorted(data.items()):
        parent_label = parent if parent else "(root)"
        click.echo(f"{name}  →  {parent_label}")
