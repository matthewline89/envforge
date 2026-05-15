"""Identify the most frequently changed keys across snapshot history."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envforge.history import get_history
from envforge.snapshot import load


@dataclass
class HotspotEntry:
    key: str
    change_count: int
    snapshots: List[str] = field(default_factory=list)


@dataclass
class HotspotReport:
    snapshot_dir: Path
    entries: List[HotspotEntry] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def top(self, n: int = 5) -> List[HotspotEntry]:
        return sorted(self.entries, key=lambda e: e.change_count, reverse=True)[:n]


def compute_hotspots(snapshot_dir: Path, top_n: int = 10) -> HotspotReport:
    """Scan history events and count how many times each key has been touched."""
    history = get_history(snapshot_dir)
    key_counts: Dict[str, int] = {}
    key_snapshots: Dict[str, List[str]] = {}

    seen_pairs: set = set()

    for event in history:
        name = event.get("snapshot", "")
        if not name:
            continue
        try:
            env = load(snapshot_dir, name)
        except Exception:
            continue
        for key in env:
            pair = (name, key)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            key_counts[key] = key_counts.get(key, 0) + 1
            key_snapshots.setdefault(key, [])
            if name not in key_snapshots[key]:
                key_snapshots[key].append(name)

    entries = [
        HotspotEntry(key=k, change_count=v, snapshots=key_snapshots.get(k, []))
        for k, v in key_counts.items()
    ]
    entries.sort(key=lambda e: e.change_count, reverse=True)

    return HotspotReport(snapshot_dir=snapshot_dir, entries=entries[:top_n])
