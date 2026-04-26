"""Diff two environment snapshots and report added, removed, and changed variables."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envforge.snapshot import load


@dataclass
class DiffResult:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)

    @property
    def is_empty(self) -> bool:
        return not (self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines: List[str] = []
        for key, value in sorted(self.added.items()):
            lines.append(f"+ {key}={value}")
        for key, value in sorted(self.removed.items()):
            lines.append(f"- {key}={value}")
        for key, (old, new) in sorted(self.changed.items()):
            lines.append(f"~ {key}: {old!r} -> {new!r}")
        return "\n".join(lines) if lines else "(no differences)"


def diff_dicts(
    before: Dict[str, str],
    after: Dict[str, str],
    ignore_keys: Optional[List[str]] = None,
) -> DiffResult:
    """Compare two env dicts and return a DiffResult."""
    ignore = set(ignore_keys or [])
    result = DiffResult()

    all_keys = set(before) | set(after)
    for key in all_keys:
        if key in ignore:
            continue
        if key not in before:
            result.added[key] = after[key]
        elif key not in after:
            result.removed[key] = before[key]
        elif before[key] != after[key]:
            result.changed[key] = (before[key], after[key])

    return result


def diff_snapshots(
    name_a: str,
    name_b: str,
    snapshot_dir: Optional[str] = None,
    ignore_keys: Optional[List[str]] = None,
) -> DiffResult:
    """Load two named snapshots and diff them."""
    kwargs = {"snapshot_dir": snapshot_dir} if snapshot_dir else {}
    before = load(name_a, **kwargs)
    after = load(name_b, **kwargs)
    return diff_dicts(before, after, ignore_keys=ignore_keys)
