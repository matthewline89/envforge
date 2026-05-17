"""CLI commands for snapshot subscriptions."""
from __future__ import annotations

from pathlib import Path

import click

from envforge.snapshot_subscription import (
    get_subscriptions,
    subscribe,
    unsubscribe,
)

DEFAULT_DIR = Path.home() / ".envforge"


@click.group("subscription")
def subscription_group() -> None:
    """Manage snapshot change subscriptions."""


@subscription_group.command("add")
@click.argument("name")
@click.option("--event", default="any", show_default=True,
              type=click.Choice(["save", "delete", "any"]),
              help="Event type to subscribe to.")
@click.option("--label", default=None, help="Optional label for this subscription.")
@click.option("--dir", "snapshot_dir", default=str(DEFAULT_DIR), show_default=True)
def add_cmd(name: str, event: str, label: str | None, snapshot_dir: str) -> None:
    """Subscribe NAME to snapshot events."""
    d = Path(snapshot_dir)
    d.mkdir(parents=True, exist_ok=True)
    is_new = subscribe(d, name, event=event, label=label)
    if is_new:
        click.echo(f"Subscribed '{name}' to '{event}' events.")
    else:
        click.echo(f"Updated subscription for '{name}' on '{event}' events.")


@subscription_group.command("remove")
@click.argument("name")
@click.option("--event", default="any", show_default=True,
              type=click.Choice(["save", "delete", "any"]))
@click.option("--dir", "snapshot_dir", default=str(DEFAULT_DIR), show_default=True)
def remove_cmd(name: str, event: str, snapshot_dir: str) -> None:
    """Unsubscribe NAME from snapshot events."""
    d = Path(snapshot_dir)
    removed = unsubscribe(d, name, event=event)
    if removed:
        click.echo(f"Removed subscription for '{name}' on '{event}' events.")
    else:
        click.echo(f"No subscription found for '{name}' on '{event}' events.")


@subscription_group.command("list")
@click.option("--dir", "snapshot_dir", default=str(DEFAULT_DIR), show_default=True)
def list_cmd(snapshot_dir: str) -> None:
    """List all active subscriptions."""
    report = get_subscriptions(Path(snapshot_dir))
    if report.is_empty():
        click.echo("No subscriptions registered.")
        return
    for entry in report.entries:
        label_part = f"  [{entry.label}]" if entry.label else ""
        click.echo(f"{entry.name}  event={entry.event}{label_part}")
