"""CLI commands for snapshot digest operations."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_digest import digest_snapshot, digests_match, find_duplicates

DEFAULT_DIR = Path.home() / ".envforge" / "snapshots"


@click.group("digest")
def digest_group() -> None:
    """Content-based digest utilities for snapshots."""


@digest_group.command("show")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def show_cmd(name: str, snap_dir: str) -> None:
    """Print the SHA-256 digest for a snapshot."""
    info = digest_snapshot(Path(snap_dir), name)
    click.echo(f"{info.name}  {info.digest}  ({info.key_count} keys)")


@digest_group.command("match")
@click.argument("name_a")
@click.argument("name_b")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def match_cmd(name_a: str, name_b: str, snap_dir: str) -> None:
    """Check whether two snapshots have identical content."""
    if digests_match(Path(snap_dir), name_a, name_b):
        click.echo(f"{name_a} and {name_b} are identical.")
    else:
        click.echo(f"{name_a} and {name_b} differ.")


@digest_group.command("duplicates")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def duplicates_cmd(snap_dir: str) -> None:
    """List groups of snapshots that share identical content."""
    groups = find_duplicates(Path(snap_dir))
    if not groups:
        click.echo("No duplicate snapshots found.")
        return
    for digest, names in groups.items():
        click.echo(f"[{digest[:12]}]  " + "  ".join(names))
