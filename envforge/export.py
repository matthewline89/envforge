"""Export snapshots to various formats (dotenv, JSON, YAML, shell)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Literal

from envforge.snapshot import load

ExportFormat = Literal["dotenv", "json", "yaml", "shell"]


def _escape(value: str) -> str:
    """Escape double quotes in a value for shell/dotenv output."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def export_dotenv(env: Dict[str, str]) -> str:
    """Render env dict as .env file content."""
    lines = [f'{k}="{_escape(v)}"' for k, v in sorted(env.items())]
    return "\n".join(lines) + "\n"


def export_json(env: Dict[str, str]) -> str:
    """Render env dict as pretty JSON."""
    return json.dumps(env, indent=2, sort_keys=True) + "\n"


def export_yaml(env: Dict[str, str]) -> str:
    """Render env dict as YAML (no external dependency)."""
    lines = [f'{k}: "{_escape(v)}"' for k, v in sorted(env.items())]
    return "\n".join(lines) + "\n"


def export_shell(env: Dict[str, str]) -> str:
    """Render env dict as export statements."""
    lines = [f'export {k}="{_escape(v)}"' for k, v in sorted(env.items())]
    return "\n".join(lines) + "\n"


_FORMATTERS = {
    "dotenv": export_dotenv,
    "json": export_json,
    "yaml": export_yaml,
    "shell": export_shell,
}


def export_snapshot(
    snapshot_name: str,
    fmt: ExportFormat,
    snapshot_dir: Path,
) -> str:
    """Load a snapshot and return its content rendered in *fmt* format."""
    if fmt not in _FORMATTERS:
        raise ValueError(f"Unsupported format: {fmt!r}. Choose from {list(_FORMATTERS)}.")
    env = load(snapshot_name, snapshot_dir)
    return _FORMATTERS[fmt](env)


def export_to_file(
    snapshot_name: str,
    fmt: ExportFormat,
    output_path: Path,
    snapshot_dir: Path,
) -> Path:
    """Export snapshot to *output_path* and return the resolved path."""
    content = export_snapshot(snapshot_name, fmt, snapshot_dir)
    output_path = Path(output_path)
    output_path.write_text(content, encoding="utf-8")
    return output_path
