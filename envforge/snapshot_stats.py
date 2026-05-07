"""Compute statistics about a snapshot's environment variables."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envforge.snapshot import load


@dataclass
class SnapshotStats:
    name: str
    total_keys: int
    empty_values: List[str] = field(default_factory=list)
    longest_key: str = ""
    longest_value_key: str = ""
    key_lengths: Dict[str, int] = field(default_factory=dict)
    value_lengths: Dict[str, int] = field(default_factory=dict)

    @property
    def empty_count(self) -> int:
        return len(self.empty_values)

    @property
    def avg_key_length(self) -> float:
        if not self.key_lengths:
            return 0.0
        return sum(self.key_lengths.values()) / len(self.key_lengths)

    @property
    def avg_value_length(self) -> float:
        if not self.value_lengths:
            return 0.0
        return sum(self.value_lengths.values()) / len(self.value_lengths)


def compute_stats(snapshot_dir: Path, name: str) -> SnapshotStats:
    """Load *name* from *snapshot_dir* and return a :class:`SnapshotStats`."""
    env: Dict[str, str] = load(snapshot_dir, name)

    key_lengths = {k: len(k) for k in env}
    value_lengths = {k: len(v) for k, v in env.items()}
    empty_values = [k for k, v in env.items() if v == ""]

    longest_key = max(key_lengths, key=key_lengths.get, default="")
    longest_value_key = max(value_lengths, key=value_lengths.get, default="")

    return SnapshotStats(
        name=name,
        total_keys=len(env),
        empty_values=empty_values,
        longest_key=longest_key,
        longest_value_key=longest_value_key,
        key_lengths=key_lengths,
        value_lengths=value_lengths,
    )


def summary(stats: SnapshotStats) -> str:
    """Return a human-readable summary of *stats*."""
    lines = [
        f"Snapshot : {stats.name}",
        f"Total keys       : {stats.total_keys}",
        f"Empty values     : {stats.empty_count}",
        f"Avg key length   : {stats.avg_key_length:.1f}",
        f"Avg value length : {stats.avg_value_length:.1f}",
    ]
    if stats.longest_key:
        lines.append(f"Longest key      : {stats.longest_key} ({stats.key_lengths[stats.longest_key]} chars)")
    if stats.longest_value_key:
        lines.append(
            f"Longest value    : {stats.longest_value_key} "
            f"({stats.value_lengths[stats.longest_value_key]} chars)"
        )
    return "\n".join(lines)
