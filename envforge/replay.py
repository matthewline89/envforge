"""Replay a snapshot's environment variables into a new snapshot with optional transformations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from envforge.snapshot import load, save


class ReplayError(Exception):
    """Raised when a replay operation fails."""

    def __str__(self) -> str:  # pragma: no cover
        return self.args[0]


@dataclass
class ReplayResult:
    source: str
    destination: str
    applied_transforms: List[str] = field(default_factory=list)
    skipped_keys: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)


def replay_snapshot(
    source: str,
    destination: str,
    snapshot_dir: str,
    *,
    prefix_filter: Optional[str] = None,
    key_transform: Optional[Callable[[str], str]] = None,
    value_transform: Optional[Callable[[str], str]] = None,
    exclude_keys: Optional[List[str]] = None,
) -> ReplayResult:
    """Load *source*, apply transforms, and save as *destination*."""
    source_env = load(source, snapshot_dir)
    if source_env is None:
        raise ReplayError(f"Snapshot '{source}' not found in {snapshot_dir}")

    exclude = set(exclude_keys or [])
    result_env: Dict[str, str] = {}
    applied: List[str] = []
    skipped: List[str] = []

    for key, value in source_env.items():
        if key in exclude:
            skipped.append(key)
            continue
        if prefix_filter and not key.startswith(prefix_filter):
            skipped.append(key)
            continue

        new_key = key_transform(key) if key_transform else key
        new_value = value_transform(value) if value_transform else value
        result_env[new_key] = new_value

        if new_key != key or new_value != value:
            applied.append(new_key)

    save(destination, result_env, snapshot_dir)
    return ReplayResult(
        source=source,
        destination=destination,
        applied_transforms=applied,
        skipped_keys=skipped,
        env=result_env,
    )
