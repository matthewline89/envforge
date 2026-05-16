"""CLI commands for snapshot categories."""
import click
from pathlib import Path

from envforge.snapshot_category import (
    add_to_category,
    remove_from_category,
    list_categories,
    get_category_members,
    find_categories_for,
    delete_category,
)

DEFAULT_DIR = Path.home() / ".envforge"


@click.group("category")
def category_group() -> None:
    """Manage snapshot categories."""


@category_group.command("add")
@click.argument("category")
@click.argument("snapshot")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def add_cmd(category: str, snapshot: str, snap_dir: str) -> None:
    """Add SNAPSHOT to CATEGORY."""
    added = add_to_category(Path(snap_dir), category, snapshot)
    if added:
        click.echo(f"Added '{snapshot}' to category '{category}'.")
    else:
        click.echo(f"'{snapshot}' is already in category '{category}'.")


@category_group.command("remove")
@click.argument("category")
@click.argument("snapshot")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def remove_cmd(category: str, snapshot: str, snap_dir: str) -> None:
    """Remove SNAPSHOT from CATEGORY."""
    removed = remove_from_category(Path(snap_dir), category, snapshot)
    if removed:
        click.echo(f"Removed '{snapshot}' from category '{category}'.")
    else:
        click.echo(f"'{snapshot}' was not found in category '{category}'.")


@category_group.command("list")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def list_cmd(snap_dir: str) -> None:
    """List all categories."""
    cats = list_categories(Path(snap_dir))
    if not cats:
        click.echo("No categories defined.")
    else:
        for cat in cats:
            click.echo(cat)


@category_group.command("show")
@click.argument("category")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def show_cmd(category: str, snap_dir: str) -> None:
    """Show members of CATEGORY."""
    members = get_category_members(Path(snap_dir), category)
    if not members:
        click.echo(f"Category '{category}' is empty or does not exist.")
    else:
        for m in members:
            click.echo(m)


@category_group.command("find")
@click.argument("snapshot")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def find_cmd(snapshot: str, snap_dir: str) -> None:
    """Find all categories containing SNAPSHOT."""
    cats = find_categories_for(Path(snap_dir), snapshot)
    if not cats:
        click.echo(f"'{snapshot}' is not in any category.")
    else:
        for cat in cats:
            click.echo(cat)


@category_group.command("delete")
@click.argument("category")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR), show_default=True)
def delete_cmd(category: str, snap_dir: str) -> None:
    """Delete an entire CATEGORY."""
    deleted = delete_category(Path(snap_dir), category)
    if deleted:
        click.echo(f"Deleted category '{category}'.")
    else:
        click.echo(f"Category '{category}' does not exist.")
