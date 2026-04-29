"""Import environment variables from external formats into envforge snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import yaml


class ImportError(Exception):
    """Raised when an import operation fails."""


def import_dotenv(source: str) -> Dict[str, str]:
    """Parse a .env file string and return a dict of key-value pairs."""
    env: Dict[str, str] = {}
    for line in source.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip surrounding quotes
        if len(value) >= 2 and value[0] in ('"', "'") and value[0] == value[-1]:
            value = value[1:-1]
        if key:
            env[key] = value
    return env


def import_json(source: str) -> Dict[str, str]:
    """Parse a JSON string and return a flat dict of string values."""
    try:
        data = json.loads(source)
    except json.JSONDecodeError as exc:
        raise ImportError(f"Invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ImportError("JSON root must be an object")
    return {str(k): str(v) for k, v in data.items()}


def import_yaml(source: str) -> Dict[str, str]:
    """Parse a YAML string and return a flat dict of string values."""
    try:
        data = yaml.safe_load(source)
    except yaml.YAMLError as exc:
        raise ImportError(f"Invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ImportError("YAML root must be a mapping")
    return {str(k): str(v) for k, v in data.items()}


def import_file(path: Path) -> Dict[str, str]:
    """Detect format from file extension and import accordingly."""
    suffix = path.suffix.lower()
    source = path.read_text(encoding="utf-8")
    if suffix in (".env", ".txt", ""):
        return import_dotenv(source)
    elif suffix == ".json":
        return import_json(source)
    elif suffix in (".yml", ".yaml"):
        return import_yaml(source)
    else:
        raise ImportError(f"Unsupported file extension: {suffix!r}")
