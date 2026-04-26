"""CLI commands for snapshot management (save, load, list, delete)."""

from __future__ import annotations

import click

from envforge import snapshot as snap_mod


@click.group("snapshot")
def snapshot_group():
    """Manage environment variable snapshots."""


@snapshot_group.command("save")
@click.argument("name")
def save_cmd(name: str):
    """Snapshot the current environment as NAME."""
    snapshot = snap_mod.capture(name)
    path = snap_mod.save(snapshot)
    var_count = len(snapshot["variables"])
    click.echo(
        click.style("✔", fg="green")
        + f" Saved snapshot '{name}' with {var_count} variables → {path}"
    )


@snapshot_group.command("list")
def list_cmd():
    """List all saved snapshots."""
    snapshots = snap_mod.list_snapshots()
    if not snapshots:
        click.echo("No snapshots found. Run 'envforge snapshot save <name>' to create one.")
        return
    click.echo(f"{'NAME':<30} {'CREATED':<32} {'VARS':>4}")
    click.echo("-" * 68)
    for s in snapshots:
        click.echo(f"{s['name']:<30} {s['created_at']:<32} {s['var_count']:>4}")


@snapshot_group.command("show")
@click.argument("name")
@click.option("--filter", "filter_prefix", default="", help="Only show vars starting with PREFIX.")
def show_cmd(name: str, filter_prefix: str):
    """Display variables stored in snapshot NAME."""
    try:
        data = snap_mod.load(name)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    variables = data["variables"]
    if filter_prefix:
        variables = {k: v for k, v in variables.items() if k.startswith(filter_prefix)}

    click.echo(f"Snapshot: {data['name']}  (created {data['created_at']})")
    click.echo(f"{'VARIABLE':<40} VALUE")
    click.echo("-" * 72)
    for key, value in sorted(variables.items()):
        display_val = value if len(value) <= 60 else value[:57] + "..."
        click.echo(f"{key:<40} {display_val}")


@snapshot_group.command("delete")
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to delete this snapshot?")
def delete_cmd(name: str):
    """Delete snapshot NAME."""
    try:
        snap_mod.delete(name)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(click.style("✔", fg="green") + f" Snapshot '{name}' deleted.")
