"""Rename snapshots with optional alias/tag migration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class RenameError(Exception):
    """Raised when a rename operation cannot be completed."""


def rename_snapshot(
    snapshot_dir: Path,
    old_name: str,
    new_name: str,
    *,
    migrate_tags: bool = True,
    migrate_aliases: bool = True,
) -> Path:
    """Rename a snapshot file and optionally migrate tags and aliases.

    Args:
        snapshot_dir: Directory containing snapshots.
        old_name: Current snapshot name (without .json extension).
        new_name: Desired snapshot name (without .json extension).
        migrate_tags: If True, update tags pointing to old_name.
        migrate_aliases: If True, update aliases pointing to old_name.

    Returns:
        Path to the renamed snapshot file.

    Raises:
        RenameError: If old snapshot does not exist or new name is taken.
    """
    old_path = snapshot_dir / f"{old_name}.json"
    new_path = snapshot_dir / f"{new_name}.json"

    if not old_path.exists():
        raise RenameError(f"Snapshot '{old_name}' does not exist.")
    if new_path.exists():
        raise RenameError(f"Snapshot '{new_name}' already exists.")

    old_path.rename(new_path)

    if migrate_tags:
        _migrate_json_values(snapshot_dir / "tags.json", old_name, new_name)

    if migrate_aliases:
        _migrate_json_values(snapshot_dir / "aliases.json", old_name, new_name)

    return new_path


def _migrate_json_values(path: Path, old_value: str, new_value: str) -> None:
    """Replace occurrences of old_value with new_value in a JSON mapping file."""
    if not path.exists():
        return

    data: dict = json.loads(path.read_text())
    updated = {k: (new_value if v == old_value else v) for k, v in data.items()}
    path.write_text(json.dumps(updated, indent=2))
