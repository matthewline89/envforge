"""CLI commands for snapshot ratings."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_rating import (
    RatingError,
    get_rating,
    list_ratings,
    remove_rating,
    set_rating,
    top_rated,
)

DEFAULT_DIR = Path.home() / ".envforge"


@click.group("rating")
def rating_group() -> None:
    """Rate and browse snapshot ratings."""


@rating_group.command("set")
@click.argument("name")
@click.argument("stars", type=int)
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR))
def set_cmd(name: str, stars: int, snap_dir: str) -> None:
    """Rate a snapshot 1–5 stars."""
    try:
        is_new = set_rating(Path(snap_dir), name, stars)
    except RatingError as exc:
        raise click.ClickException(str(exc))
    action = "Rated" if is_new else "Updated rating for"
    click.echo(f"{action} '{name}': {'★' * stars}{'☆' * (5 - stars)} ({stars}/5)")


@rating_group.command("remove")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR))
def remove_cmd(name: str, snap_dir: str) -> None:
    """Remove a snapshot's rating."""
    found = remove_rating(Path(snap_dir), name)
    if found:
        click.echo(f"Removed rating for '{name}'.")
    else:
        click.echo(f"No rating found for '{name}'.")


@rating_group.command("show")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR))
def show_cmd(name: str, snap_dir: str) -> None:
    """Show the rating for a snapshot."""
    stars = get_rating(Path(snap_dir), name)
    if stars is None:
        click.echo(f"No rating for '{name}'.")
    else:
        click.echo(f"{name}: {'★' * stars}{'☆' * (5 - stars)} ({stars}/5)")


@rating_group.command("list")
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR))
def list_cmd(snap_dir: str) -> None:
    """List all rated snapshots."""
    ratings = list_ratings(Path(snap_dir))
    if not ratings:
        click.echo("No ratings recorded.")
        return
    for name, stars in sorted(ratings.items()):
        click.echo(f"  {name}: {'★' * stars}{'☆' * (5 - stars)}")


@rating_group.command("top")
@click.option("--limit", default=5, show_default=True)
@click.option("--dir", "snap_dir", default=str(DEFAULT_DIR))
def top_cmd(limit: int, snap_dir: str) -> None:
    """Show top-rated snapshots."""
    results = top_rated(Path(snap_dir), limit=limit)
    if not results:
        click.echo("No ratings recorded.")
        return
    for entry in results:
        click.echo(f"  {entry.name}: {'★' * entry.stars}{'☆' * (5 - entry.stars)}")
