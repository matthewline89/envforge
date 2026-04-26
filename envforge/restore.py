"""Restore environment variable snapshots to shell-sourceable scripts."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from envforge.snapshot import load


SHELL_FORMATS = ("bash", "zsh", "fish", "env")


def generate_export_script(env: dict[str, str], shell: str = "bash") -> str:
    """Generate a shell script that exports the given environment variables."""
    if shell not in SHELL_FORMATS:
        raise ValueError(f"Unsupported shell format '{shell}'. Choose from: {', '.join(SHELL_FORMATS)}")

    lines: list[str] = []

    if shell in ("bash", "zsh"):
        lines.append("#!/usr/bin/env " + shell)
        for key, value in sorted(env.items()):
            escaped = value.replace('"', '\\"')
            lines.append(f'export {key}="{escaped}"')

    elif shell == "fish":
        for key, value in sorted(env.items()):
            escaped = value.replace('"', '\\"')
            lines.append(f'set -x {key} "{escaped}"')

    elif shell == "env":
        for key, value in sorted(env.items()):
            lines.append(f"{key}={value}")

    return "\n".join(lines) + "\n"


def restore_to_file(
    name: str,
    output_path: Path,
    shell: str = "bash",
    snapshot_dir: Optional[Path] = None,
) -> dict[str, str]:
    """Load a snapshot and write an export script to output_path.

    Returns the loaded environment dict.
    """
    env = load(name, snapshot_dir=snapshot_dir)
    script = generate_export_script(env, shell=shell)
    output_path.write_text(script)
    return env


def apply_to_current_process(
    name: str,
    snapshot_dir: Optional[Path] = None,
    overwrite: bool = False,
) -> dict[str, str]:
    """Apply a snapshot's variables to the current process environment.

    Returns the dict of variables that were applied.
    """
    env = load(name, snapshot_dir=snapshot_dir)
    applied: dict[str, str] = {}
    for key, value in env.items():
        if overwrite or key not in os.environ:
            os.environ[key] = value
            applied[key] = value
    return applied
