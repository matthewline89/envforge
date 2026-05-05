"""CLI commands for snapshot validation."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import click

from envforge.validate import validate_snapshot


@click.group("validate")
def validate_group() -> None:
    """Validate snapshot contents against rules."""


@validate_group.command("run")
@click.argument("name")
@click.option(
    "--snapshot-dir",
    default=".envforge",
    show_default=True,
    help="Directory where snapshots are stored.",
)
@click.option(
    "--require",
    "required_keys",
    multiple=True,
    metavar="KEY",
    help="Keys that must be present (repeatable).",
)
@click.option(
    "--forbid",
    "forbidden_keys",
    multiple=True,
    metavar="KEY",
    help="Keys that must not be present (repeatable).",
)
@click.option(
    "--pattern",
    "key_pattern",
    default=None,
    help="Regex pattern every key must match (e.g. '^[A-Z_]+$').",
)
@click.option("--strict", is_flag=True, help="Exit non-zero on warnings too.")
def run_cmd(
    name: str,
    snapshot_dir: str,
    required_keys: List[str],
    forbidden_keys: List[str],
    key_pattern: Optional[str],
    strict: bool,
) -> None:
    """Validate snapshot NAME and report issues."""
    snap_path = Path(snapshot_dir)
    try:
        report = validate_snapshot(
            snap_path,
            name,
            required_keys=list(required_keys) or None,
            forbidden_keys=list(forbidden_keys) or None,
            key_pattern=key_pattern,
        )
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found in {snapshot_dir}.")

    click.echo(report.summary())

    if not report.is_valid:
        raise click.ClickException("Validation failed with errors.")
    if strict and report.has_warnings:
        raise click.ClickException("Validation failed: warnings present (--strict mode).")
