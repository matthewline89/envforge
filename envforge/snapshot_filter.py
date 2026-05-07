"""Filter snapshots by key patterns, value patterns, or metadata criteria."""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from envforge.snapshot import load, list_snapshots


@dataclass
class FilterResult:
    matched: list[str] = field(default_factory=list)
    total_scanned: int = 0

    def __len__(self) -> int:
        return len(self.matched)

    def is_empty(self) -> bool:
        return len(self.matched) == 0


def _matches_pattern(value: str, pattern: str) -> bool:
    """Return True if value matches glob-style pattern (case-insensitive)."""
    return fnmatch.fnmatch(value.lower(), pattern.lower())


def filter_by_key(
    snapshot_dir: Path,
    key_pattern: str,
) -> FilterResult:
    """Return snapshots that contain at least one key matching key_pattern."""
    names = list_snapshots(snapshot_dir)
    matched: list[str] = []
    for name in names:
        env = load(snapshot_dir, name)
        if any(_matches_pattern(k, key_pattern) for k in env):
            matched.append(name)
    return FilterResult(matched=matched, total_scanned=len(names))


def filter_by_value(
    snapshot_dir: Path,
    value_pattern: str,
) -> FilterResult:
    """Return snapshots that contain at least one value matching value_pattern."""
    names = list_snapshots(snapshot_dir)
    matched: list[str] = []
    for name in names:
        env = load(snapshot_dir, name)
        if any(_matches_pattern(v, value_pattern) for v in env.values()):
            matched.append(name)
    return FilterResult(matched=matched, total_scanned=len(names))


def filter_by_predicate(
    snapshot_dir: Path,
    predicate: Callable[[dict[str, str]], bool],
) -> FilterResult:
    """Return snapshots for which predicate(env_dict) returns True."""
    names = list_snapshots(snapshot_dir)
    matched: list[str] = []
    for name in names:
        env = load(snapshot_dir, name)
        if predicate(env):
            matched.append(name)
    return FilterResult(matched=matched, total_scanned=len(names))


def filter_by_size(
    snapshot_dir: Path,
    min_keys: int = 0,
    max_keys: int | None = None,
) -> FilterResult:
    """Return snapshots whose key count is within [min_keys, max_keys]."""
    def _size_pred(env: dict[str, str]) -> bool:
        n = len(env)
        if n < min_keys:
            return False
        if max_keys is not None and n > max_keys:
            return False
        return True

    return filter_by_predicate(snapshot_dir, _size_pred)
