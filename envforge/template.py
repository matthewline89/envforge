"""Template management for envforge: create and apply env templates with placeholders."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

TEMPLATE_SUFFIX = ".template.json"
_PLACEHOLDER_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def _template_path(snapshot_dir: Path, name: str) -> Path:
    return snapshot_dir / f"{name}{TEMPLATE_SUFFIX}"


def create_template(env: dict[str, str], snapshot_dir: Path, name: str) -> Path:
    """Save *env* as a template, replacing values that look like secrets with placeholders."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    template: dict[str, str] = {}
    for key, value in env.items():
        template[key] = f"{{{{ {key} }}}}"
    path = _template_path(snapshot_dir, name)
    path.write_text(json.dumps(template, indent=2), encoding="utf-8")
    return path


def load_template(snapshot_dir: Path, name: str) -> dict[str, str]:
    """Load a previously saved template."""
    path = _template_path(snapshot_dir, name)
    if not path.exists():
        raise FileNotFoundError(f"Template '{name}' not found at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def list_templates(snapshot_dir: Path) -> list[str]:
    """Return the names of all saved templates."""
    if not snapshot_dir.exists():
        return []
    return [
        p.name[: -len(TEMPLATE_SUFFIX)]
        for p in sorted(snapshot_dir.iterdir())
        if p.name.endswith(TEMPLATE_SUFFIX)
    ]


def apply_template(template: dict[str, str], values: dict[str, str]) -> dict[str, str]:
    """Substitute *values* into *template* placeholders and return the resolved env dict."""
    resolved: dict[str, str] = {}
    missing: list[str] = []
    for key, tmpl_value in template.items():
        match = _PLACEHOLDER_RE.fullmatch(tmpl_value)
        if match:
            placeholder = match.group(1)
            if placeholder not in values:
                missing.append(placeholder)
            else:
                resolved[key] = values[placeholder]
        else:
            resolved[key] = tmpl_value
    if missing:
        raise KeyError(f"Missing values for placeholders: {missing}")
    return resolved


def delete_template(snapshot_dir: Path, name: str) -> bool:
    """Delete a template. Returns True if it existed, False otherwise."""
    path = _template_path(snapshot_dir, name)
    if path.exists():
        path.unlink()
        return True
    return False
