"""Search across snapshots for keys or values matching a pattern."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envforge.snapshot import load, list_snapshots


@dataclass
class SearchMatch:
    snapshot_name: str
    key: str
    value: str


@dataclass
class SearchResult:
    matches: list[SearchMatch] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.matches) == 0

    def grouped_by_snapshot(self) -> dict[str, list[SearchMatch]]:
        groups: dict[str, list[SearchMatch]] = {}
        for match in self.matches:
            groups.setdefault(match.snapshot_name, []).append(match)
        return groups


def search_snapshots(
    pattern: str,
    snapshot_dir: Path,
    search_keys: bool = True,
    search_values: bool = True,
    snapshot_name: Optional[str] = None,
    case_sensitive: bool = False,
) -> SearchResult:
    """Search for a regex pattern across snapshot keys and/or values."""
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        compiled = re.compile(pattern, flags)
    except re.error as exc:
        raise ValueError(f"Invalid regex pattern '{pattern}': {exc}") from exc

    result = SearchResult()

    if snapshot_name:
        names = [snapshot_name]
    else:
        names = list_snapshots(snapshot_dir)

    for name in names:
        try:
            env = load(name, snapshot_dir)
        except FileNotFoundError:
            continue

        for key, value in env.items():
            key_matches = search_keys and compiled.search(key) is not None
            value_matches = search_values and compiled.search(value) is not None
            if key_matches or value_matches:
                result.matches.append(SearchMatch(snapshot_name=name, key=key, value=value))

    return result
