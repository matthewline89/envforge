"""Compute and compare size metrics for snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envforge.snapshot import load, list_snapshots


@dataclass
class SizeInfo:
    name: str
    key_count: int
    total_chars: int
    largest_key: str
    largest_value_key: str


@dataclass
class SizeReport:
    entries: List[SizeInfo] = field(default_factory=list)


def _total_chars(env: dict) -> int:
    return sum(len(k) + len(v) for k, v in env.items())


def _largest_key(env: dict) -> str:
    if not env:
        return ""
    return max(env.keys(), key=len)


def _largest_value_key(env: dict) -> str:
    if not env:
        return ""
    return max(env.keys(), key=lambda k: len(env[k]))


def size_snapshot(name: str, snapshot_dir: Path) -> SizeInfo:
    """Return size metrics for a single snapshot."""
    env = load(name, snapshot_dir)
    return SizeInfo(
        name=name,
        key_count=len(env),
        total_chars=_total_chars(env),
        largest_key=_largest_key(env),
        largest_value_key=_largest_value_key(env),
    )


def size_report(snapshot_dir: Path) -> SizeReport:
    """Return size metrics for all snapshots in *snapshot_dir*."""
    names = list_snapshots(snapshot_dir)
    entries = [size_snapshot(n, snapshot_dir) for n in names]
    return SizeReport(entries=entries)


def largest_snapshot(report: SizeReport) -> SizeInfo | None:
    """Return the entry with the highest total character count."""
    if not report.entries:
        return None
    return max(report.entries, key=lambda e: e.total_chars)


def smallest_snapshot(report: SizeReport) -> SizeInfo | None:
    """Return the entry with the lowest total character count."""
    if not report.entries:
        return None
    return min(report.entries, key=lambda e: e.total_chars)
