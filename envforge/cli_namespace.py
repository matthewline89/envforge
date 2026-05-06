"""CLI commands for namespace management."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.namespace import (
    add_to_namespace,
    list_namespaces,
    members_of,
    namespace_of,
    remove_from_namespace,
)

_DEFAULT_DIR = Path.home() / ".envforge"


@click.group("namespace")
def namespace_group() -> None:
    """Organise snapshots into named namespaces."""


@namespace_group.command("add")
@click.argument("namespace")
@click.argument("snapshot")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def add_cmd(namespace: str, snapshot: str, snap_dir: str) -> None:
    """Add SNAPSHOT to NAMESPACE."""
    added = add_to_namespace(Path(snap_dir), namespace, snapshot)
    if added:
        click.echo(f"Added '{snapshot}' to namespace '{namespace}'.")
    else:
        click.echo(f"'{snapshot}' is already in namespace '{namespace}'.")


@namespace_group.command("remove")
@click.argument("namespace")
@click.argument("snapshot")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def remove_cmd(namespace: str, snapshot: str, snap_dir: str) -> None:
    """Remove SNAPSHOT from NAMESPACE."""
    removed = remove_from_namespace(Path(snap_dir), namespace, snapshot)
    if removed:
        click.echo(f"Removed '{snapshot}' from namespace '{namespace}'.")
    else:
        click.echo(f"'{snapshot}' was not found in namespace '{namespace}'.")


@namespace_group.command("list")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def list_cmd(snap_dir: str) -> None:
    """List all namespaces."""
    names = list_namespaces(Path(snap_dir))
    if not names:
        click.echo("No namespaces defined.")
        return
    for name in names:
        click.echo(name)


@namespace_group.command("show")
@click.argument("namespace")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def show_cmd(namespace: str, snap_dir: str) -> None:
    """Show snapshots belonging to NAMESPACE."""
    members = members_of(Path(snap_dir), namespace)
    if not members:
        click.echo(f"Namespace '{namespace}' is empty or does not exist.")
        return
    for m in members:
        click.echo(m)


@namespace_group.command("resolve")
@click.argument("snapshot")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def resolve_cmd(snapshot: str, snap_dir: str) -> None:
    """Print the namespace that owns SNAPSHOT."""
    ns = namespace_of(Path(snap_dir), snapshot)
    if ns is None:
        click.echo(f"'{snapshot}' does not belong to any namespace.")
    else:
        click.echo(ns)
