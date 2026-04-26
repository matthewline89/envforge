"""CLI commands for restoring environment snapshots."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

from envforge.restore import SHELL_FORMATS, generate_export_script, restore_to_file
from envforge.snapshot import load


@click.group(name="restore")
def restore_group() -> None:
    """Restore environment variable snapshots."""


@restore_group.command(name="export")
@click.argument("name")
@click.option(
    "--shell",
    default="bash",
    show_default=True,
    type=click.Choice(SHELL_FORMATS, case_sensitive=False),
    help="Target shell format for the export script.",
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    help="Write script to this file instead of stdout.",
)
@click.option(
    "--snapshot-dir",
    default=None,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Custom directory where snapshots are stored.",
)
def export_cmd(
    name: str,
    shell: str,
    output: Optional[Path],
    snapshot_dir: Optional[Path],
) -> None:
    """Generate a shell export script from snapshot NAME."""
    try:
        if output:
            env = restore_to_file(name, output, shell=shell, snapshot_dir=snapshot_dir)
            click.echo(f"Wrote {len(env)} variable(s) to {output}")
        else:
            env = load(name, snapshot_dir=snapshot_dir)
            script = generate_export_script(env, shell=shell)
            click.echo(script, nl=False)
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found.")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@restore_group.command(name="apply")
@click.argument("name")
@click.option(
    "--snapshot-dir",
    default=None,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Custom directory where snapshots are stored.",
)
def apply_cmd(name: str, snapshot_dir: Optional[Path]) -> None:
    """Print eval-able export commands to apply snapshot NAME to the current shell.

    Usage: eval $(envforge restore apply <name>)
    """
    try:
        env = load(name, snapshot_dir=snapshot_dir)
        script = generate_export_script(env, shell="bash")
        click.echo(script, nl=False)
    except FileNotFoundError:
        raise click.ClickException(f"Snapshot '{name}' not found.")
