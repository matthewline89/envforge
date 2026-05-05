"""Clone (deep-copy) an existing snapshot under a new name."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envforge.snapshot import load, save


class CloneError(Exception):
    """Raised when a clone operation cannot be completed."""


def clone_snapshot(
    source: str,
    dest: str,
    snapshot_dir: Path,
    overwrite: bool = False,
    note: Optional[str] = None,
) -> Path:
    """Copy *source* snapshot to *dest* inside *snapshot_dir*.

    Parameters
    ----------
    source:
        Name of the existing snapshot to copy from.
    dest:
        Name for the new snapshot.
    snapshot_dir:
        Directory that holds all snapshot JSON files.
    overwrite:
        When *True* silently replace an existing *dest* snapshot.
    note:
        Optional metadata note stored under the ``_clone_note`` key.

    Returns
    -------
    Path
        Absolute path to the newly created snapshot file.
    """
    src_path = snapshot_dir / f"{source}.json"
    dst_path = snapshot_dir / f"{dest}.json"

    if not src_path.exists():
        raise CloneError(f"Source snapshot '{source}' does not exist.")

    if dst_path.exists() and not overwrite:
        raise CloneError(
            f"Destination snapshot '{dest}' already exists. "
            "Use overwrite=True to replace it."
        )

    env = load(source, snapshot_dir)

    if note is not None:
        env = {**env, "_clone_note": note}

    saved = save(dest, env, snapshot_dir)
    return saved
