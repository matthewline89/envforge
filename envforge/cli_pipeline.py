"""CLI commands for pipeline management."""
import click
from pathlib import Path
from envforge.pipeline import (
    create_pipeline,
    get_pipeline,
    list_pipelines,
    delete_pipeline,
    append_step,
    PipelineError,
)


@click.group(name="pipeline")
def pipeline_group():
    """Manage snapshot pipelines."""


@pipeline_group.command(name="create")
@click.argument("name")
@click.argument("steps", nargs=-1, required=True)
@click.option("--description", "-d", default="", help="Pipeline description")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def create_cmd(name, steps, description, snapshot_dir):
    """Create a new pipeline with ordered snapshot STEPS."""
    d = Path(snapshot_dir)
    d.mkdir(parents=True, exist_ok=True)
    try:
        p = create_pipeline(d, name, list(steps), description)
        click.echo(f"Pipeline '{p.name}' created with {len(p.steps)} step(s).")
    except PipelineError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@pipeline_group.command(name="show")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def show_cmd(name, snapshot_dir):
    """Show steps in a pipeline."""
    try:
        p = get_pipeline(Path(snapshot_dir), name)
        if p.description:
            click.echo(f"Description: {p.description}")
        for i, step in enumerate(p.steps, 1):
            click.echo(f"  {i}. {step}")
    except PipelineError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@pipeline_group.command(name="list")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def list_cmd(snapshot_dir):
    """List all pipelines."""
    pipelines = list_pipelines(Path(snapshot_dir))
    if not pipelines:
        click.echo("No pipelines defined.")
        return
    for p in pipelines:
        step_count = len(p.steps)
        click.echo(f"{p.name}  ({step_count} step{'s' if step_count != 1 else ''})")


@pipeline_group.command(name="append")
@click.argument("name")
@click.argument("snapshot_name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def append_cmd(name, snapshot_name, snapshot_dir):
    """Append SNAPSHOT_NAME as the next step in pipeline NAME."""
    try:
        p = append_step(Path(snapshot_dir), name, snapshot_name)
        click.echo(f"Appended '{snapshot_name}' to pipeline '{p.name}' (now {len(p.steps)} steps).")
    except PipelineError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@pipeline_group.command(name="delete")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
def delete_cmd(name, snapshot_dir):
    """Delete a pipeline."""
    removed = delete_pipeline(Path(snapshot_dir), name)
    if removed:
        click.echo(f"Pipeline '{name}' deleted.")
    else:
        click.echo(f"Pipeline '{name}' not found.", err=True)
        raise SystemExit(1)
