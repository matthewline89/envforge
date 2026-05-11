"""CLI commands for snapshot scoring."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_score import score_snapshot
from envforge.snapshot import list_snapshots

_DEFAULT_DIR = Path.home() / ".envforge" / "snapshots"


@click.group("score")
def score_group() -> None:
    """Score snapshots for quality."""


@score_group.command("show")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def show_cmd(name: str, snap_dir: str) -> None:
    """Show the quality score for a snapshot."""
    result = score_snapshot(name, Path(snap_dir))
    click.echo(f"Snapshot : {result.name}")
    click.echo(f"Score    : {result.score}/{result.max_score} ({result.percent}%)")
    click.echo(f"Grade    : {result.grade}")
    if result.breakdown.details:
        click.echo("Issues:")
        for d in result.breakdown.details:
            click.echo(f"  - {d}")


@score_group.command("rank")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def rank_cmd(snap_dir: str) -> None:
    """Rank all snapshots by quality score."""
    names = list_snapshots(Path(snap_dir))
    if not names:
        click.echo("No snapshots found.")
        return
    results = [score_snapshot(n, Path(snap_dir)) for n in names]
    results.sort(key=lambda r: r.score, reverse=True)
    click.echo(f"{'Rank':<5} {'Name':<30} {'Score':<12} {'Grade':<6}")
    click.echo("-" * 55)
    for i, r in enumerate(results, 1):
        click.echo(f"{i:<5} {r.name:<30} {r.score}/{r.max_score:<8} {r.grade:<6}")
