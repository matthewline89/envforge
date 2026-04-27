"""CLI commands for envforge template management."""

from __future__ import annotations

import json
from pathlib import Path

import click

from envforge import snapshot as snap
from envforge import template as tmpl

DEFAULT_DIR = Path.home() / ".envforge"


@click.group("template")
def template_group() -> None:
    """Manage environment variable templates."""


@template_group.command("create")
@click.argument("snapshot_name")
@click.argument("template_name")
@click.option("--dir", "snapshot_dir", default=str(DEFAULT_DIR), show_default=True)
def create_cmd(snapshot_name: str, template_name: str, snapshot_dir: str) -> None:
    """Create a template from an existing snapshot."""
    sdir = Path(snapshot_dir)
    env = snap.load(sdir, snapshot_name)
    path = tmpl.create_template(env, sdir, template_name)
    click.echo(f"Template '{template_name}' created at {path}")


@template_group.command("list")
@click.option("--dir", "snapshot_dir", default=str(DEFAULT_DIR), show_default=True)
def list_cmd(snapshot_dir: str) -> None:
    """List all saved templates."""
    names = tmpl.list_templates(Path(snapshot_dir))
    if not names:
        click.echo("No templates found.")
    else:
        for name in names:
            click.echo(name)


@template_group.command("show")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=str(DEFAULT_DIR), show_default=True)
def show_cmd(name: str, snapshot_dir: str) -> None:
    """Show the contents of a template."""
    data = tmpl.load_template(Path(snapshot_dir), name)
    click.echo(json.dumps(data, indent=2))


@template_group.command("apply")
@click.argument("template_name")
@click.argument("output_snapshot")
@click.option("-v", "--value", "values", multiple=True, metavar="KEY=VALUE",
              help="Placeholder values in KEY=VALUE format.")
@click.option("--dir", "snapshot_dir", default=str(DEFAULT_DIR), show_default=True)
def apply_cmd(template_name: str, output_snapshot: str, values: tuple[str, ...], snapshot_dir: str) -> None:
    """Apply values to a template and save as a new snapshot."""
    sdir = Path(snapshot_dir)
    parsed: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {item}")
        k, v = item.split("=", 1)
        parsed[k] = v
    template = tmpl.load_template(sdir, template_name)
    resolved = tmpl.apply_template(template, parsed)
    snap.save(sdir, output_snapshot, resolved)
    click.echo(f"Snapshot '{output_snapshot}' created from template '{template_name}'.")


@template_group.command("delete")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=str(DEFAULT_DIR), show_default=True)
def delete_cmd(name: str, snapshot_dir: str) -> None:
    """Delete a template."""
    removed = tmpl.delete_template(Path(snapshot_dir), name)
    if removed:
        click.echo(f"Template '{name}' deleted.")
    else:
        click.echo(f"Template '{name}' not found.", err=True)
