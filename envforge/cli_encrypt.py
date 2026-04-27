"""CLI commands for encrypted snapshot operations."""

from __future__ import annotations

from pathlib import Path

import click

from envforge import encrypt as enc
from envforge.snapshot import capture, load, save


@click.group("encrypt")
def encrypt_group() -> None:
    """Manage encrypted snapshots."""


@encrypt_group.command("keygen")
def keygen_cmd() -> None:
    """Generate a new encryption key and print it to stdout."""
    key = enc.generate_key()
    click.echo(key)
    click.echo(
        click.style(
            f"\nTip: export {enc.KEY_ENV_VAR}={key}", fg="yellow"
        ),
        err=True,
    )


@encrypt_group.command("save")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
@click.option("--key", envvar=enc.KEY_ENV_VAR, required=True, help="Fernet key")
def save_cmd(name: str, snapshot_dir: str, key: str) -> None:
    """Capture current environment and save as an encrypted snapshot."""
    data = capture()
    path = Path(snapshot_dir) / f"{name}.enc"
    path.parent.mkdir(parents=True, exist_ok=True)
    enc.save_encrypted(data, path, key)
    click.echo(f"Encrypted snapshot saved to {path}")


@encrypt_group.command("load")
@click.argument("name")
@click.option("--dir", "snapshot_dir", default=".envforge", show_default=True)
@click.option("--key", envvar=enc.KEY_ENV_VAR, required=True, help="Fernet key")
@click.option("--out", default=None, help="Save decrypted snapshot under this name")
def load_cmd(name: str, snapshot_dir: str, key: str, out: str | None) -> None:
    """Decrypt an encrypted snapshot and optionally save it as a plain snapshot."""
    path = Path(snapshot_dir) / f"{name}.enc"
    if not path.exists():
        raise click.ClickException(f"Encrypted snapshot not found: {path}")
    try:
        data = enc.load_encrypted(path, key)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    if out:
        out_path = Path(snapshot_dir) / f"{out}.json"
        save(data, out_path)
        click.echo(f"Decrypted snapshot saved to {out_path}")
    else:
        import json
        click.echo(json.dumps(data, indent=2, sort_keys=True))
