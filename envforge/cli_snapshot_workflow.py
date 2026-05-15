"""CLI commands for snapshot workflows."""
from __future__ import annotations

import click
from pathlib import Path

from envforge.snapshot_workflow import (
    WorkflowError,
    append_step,
    create_workflow,
    delete_workflow,
    get_workflow,
    list_workflows,
)

_DEFAULT_DIR = Path(".envforge")


@click.group("workflow")
def workflow_group() -> None:
    """Manage snapshot workflows."""


@workflow_group.command("create")
@click.argument("name")
@click.option("--description", "-d", default="", help="Workflow description")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def create_cmd(name: str, description: str, snap_dir: str) -> None:
    """Create a new workflow."""
    is_new = create_workflow(Path(snap_dir), name, description)
    if is_new:
        click.echo(f"Created workflow '{name}'.")
    else:
        click.echo(f"Updated workflow '{name}'.")


@workflow_group.command("append")
@click.argument("name")
@click.argument("operation")
@click.option("--param", "-p", multiple=True, help="key=value params")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def append_cmd(name: str, operation: str, param: tuple, snap_dir: str) -> None:
    """Append a step to a workflow."""
    params: dict = {}
    for p in param:
        if "=" in p:
            k, v = p.split("=", 1)
            params[k] = v
    try:
        append_step(Path(snap_dir), name, operation, params)
        click.echo(f"Appended step '{operation}' to workflow '{name}'.")
    except WorkflowError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@workflow_group.command("show")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def show_cmd(name: str, snap_dir: str) -> None:
    """Show steps in a workflow."""
    try:
        wf = get_workflow(Path(snap_dir), name)
    except WorkflowError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    click.echo(f"Workflow: {wf.name}")
    if wf.description:
        click.echo(f"Description: {wf.description}")
    if not wf.steps:
        click.echo("  (no steps)")
    for i, step in enumerate(wf.steps, 1):
        click.echo(f"  {i}. {step.operation}  {step.params}")


@workflow_group.command("list")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def list_cmd(snap_dir: str) -> None:
    """List all workflows."""
    names = list_workflows(Path(snap_dir))
    if not names:
        click.echo("No workflows found.")
    for n in names:
        click.echo(n)


@workflow_group.command("delete")
@click.argument("name")
@click.option("--dir", "snap_dir", default=str(_DEFAULT_DIR), show_default=True)
def delete_cmd(name: str, snap_dir: str) -> None:
    """Delete a workflow."""
    removed = delete_workflow(Path(snap_dir), name)
    if removed:
        click.echo(f"Deleted workflow '{name}'.")
    else:
        click.echo(f"Workflow '{name}' not found.", err=True)
        raise SystemExit(1)
