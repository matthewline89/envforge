"""CLI commands for snapshot dependency tracking."""
import click
from pathlib import Path

from envforge.snapshot_dependency import add_dependency, remove_dependency, get_report


@click.group("dependency")
def dependency_group() -> None:
    """Manage dependencies between snapshots."""


@dependency_group.command("add")
@click.argument("snapshot")
@click.argument("depends_on")
@click.option("--note", default=None, help="Optional note about the dependency.")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def add_cmd(snapshot: str, depends_on: str, note: str, snap_dir: str) -> None:
    """Record that SNAPSHOT depends on DEPENDS_ON."""
    d = Path(snap_dir)
    d.mkdir(parents=True, exist_ok=True)
    is_new = add_dependency(d, snapshot, depends_on, note)
    if is_new:
        click.echo(f"Added dependency: {snapshot} -> {depends_on}")
    else:
        click.echo(f"Dependency already exists: {snapshot} -> {depends_on}")


@dependency_group.command("remove")
@click.argument("snapshot")
@click.argument("depends_on")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def remove_cmd(snapshot: str, depends_on: str, snap_dir: str) -> None:
    """Remove a dependency edge."""
    removed = remove_dependency(Path(snap_dir), snapshot, depends_on)
    if removed:
        click.echo(f"Removed dependency: {snapshot} -> {depends_on}")
    else:
        click.echo(f"Dependency not found: {snapshot} -> {depends_on}")


@dependency_group.command("show")
@click.argument("snapshot")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def show_cmd(snapshot: str, snap_dir: str) -> None:
    """Show dependencies for a snapshot."""
    report = get_report(Path(snap_dir))
    entry = report.for_snapshot(snapshot)
    if not entry or not entry.depends_on:
        click.echo(f"No dependencies recorded for '{snapshot}'.")
        return
    click.echo(f"Dependencies of '{snapshot}':")
    for dep in entry.depends_on:
        click.echo(f"  -> {dep}")
    if entry.note:
        click.echo(f"Note: {entry.note}")


@dependency_group.command("list")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def list_cmd(snap_dir: str) -> None:
    """List all recorded dependency edges."""
    report = get_report(Path(snap_dir))
    if report.is_empty():
        click.echo("No dependencies recorded.")
        return
    for name, entry in report.entries.items():
        for dep in entry.depends_on:
            click.echo(f"{name} -> {dep}")
