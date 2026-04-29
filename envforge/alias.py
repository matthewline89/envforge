"""Alias management for envforge snapshots.

Allows users to create short, memorable aliases for snapshot names,
similar to git aliases but for environment snapshots.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

_ALIAS_FILE = "aliases.json"


def _alias_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _ALIAS_FILE


def _load_aliases(snapshot_dir: Path) -> dict[str, str]:
    path = _alias_path(snapshot_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_aliases(snapshot_dir: Path, aliases: dict[str, str]) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    _alias_path(snapshot_dir).write_text(json.dumps(aliases, indent=2))


def set_alias(snapshot_dir: Path, alias: str, snapshot_name: str) -> None:
    """Create or overwrite an alias pointing to a snapshot name."""
    aliases = _load_aliases(snapshot_dir)
    aliases[alias] = snapshot_name
    _save_aliases(snapshot_dir, aliases)


def remove_alias(snapshot_dir: Path, alias: str) -> bool:
    """Remove an alias. Returns True if it existed, False otherwise."""
    aliases = _load_aliases(snapshot_dir)
    if alias not in aliases:
        return False
    del aliases[alias]
    _save_aliases(snapshot_dir, aliases)
    return True


def resolve_alias(snapshot_dir: Path, alias: str) -> Optional[str]:
    """Return the snapshot name for the given alias, or None if not found."""
    return _load_aliases(snapshot_dir).get(alias)


def list_aliases(snapshot_dir: Path) -> dict[str, str]:
    """Return all alias -> snapshot_name mappings."""
    return _load_aliases(snapshot_dir)


def resolve_name_or_alias(snapshot_dir: Path, name_or_alias: str) -> str:
    """Resolve a name that may be either a direct snapshot name or an alias.

    Returns the resolved snapshot name. If the input is not a known alias,
    it is returned as-is (treated as a direct snapshot name).
    """
    resolved = resolve_alias(snapshot_dir, name_or_alias)
    return resolved if resolved is not None else name_or_alias
