"""CLI commands for snapshot verification."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_verify import verify_snapshot, verify_all


@click.group("verify")
def verify_group() -> None:
    """Verify snapshot integrity."""


@verify_group.command("check")
@click.argument("name")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def check_cmd(name: str, snap_dir: str) -> None:
    """Check a single snapshot for integrity issues."""
    result = verify_snapshot(name, Path(snap_dir))
    status_color = {"OK": "green", "WARN": "yellow", "FAIL": "red"}
    click.echo(
        f"[{click.style(result.status, fg=status_color.get(result.status, 'white'))}] "
        f"{result.snapshot}  digest={result.digest.digest[:12]}…"
    )
    for issue in result.issues:
        color = "red" if issue.severity == "error" else "yellow"
        click.echo(f"  {click.style(issue.severity.upper(), fg=color)}: {issue.message}")
    if result.ok and not result.issues:
        click.echo("  No issues found.")


@verify_group.command("scan")
@click.option("--dir", "snap_dir", default=".envforge", show_default=True)
def scan_cmd(snap_dir: str) -> None:
    """Verify all snapshots in the snapshot directory."""
    results = verify_all(Path(snap_dir))
    if not results:
        click.echo("No snapshots found.")
        return
    for result in results:
        status_color = {"OK": "green", "WARN": "yellow", "FAIL": "red"}
        click.echo(
            f"[{click.style(result.status, fg=status_color.get(result.status, 'white'))}] "
            f"{result.snapshot}"
        )
        for issue in result.issues:
            color = "red" if issue.severity == "error" else "yellow"
            click.echo(f"  {click.style(issue.severity.upper(), fg=color)}: {issue.message}")
    total = len(results)
    failed = sum(1 for r in results if not r.ok)
    click.echo(f"\n{total} snapshot(s) checked, {failed} failed.")
