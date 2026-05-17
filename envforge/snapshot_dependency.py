"""Track dependencies between snapshots."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DependencyEntry:
    snapshot: str
    depends_on: List[str]
    note: Optional[str] = None


@dataclass
class DependencyReport:
    entries: Dict[str, DependencyEntry] = field(default_factory=dict)

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def for_snapshot(self, name: str) -> Optional[DependencyEntry]:
        return self.entries.get(name)

    def dependents_of(self, name: str) -> List[str]:
        """Return all snapshots that depend on the given snapshot."""
        return [
            snap
            for snap, entry in self.entries.items()
            if name in entry.depends_on
        ]


def _dep_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "dependencies.json"


def _load_deps(snapshot_dir: Path) -> Dict[str, dict]:
    p = _dep_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_deps(snapshot_dir: Path, data: Dict[str, dict]) -> None:
    _dep_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def add_dependency(
    snapshot_dir: Path,
    snapshot: str,
    depends_on: str,
    note: Optional[str] = None,
) -> bool:
    """Add a dependency edge. Returns True if new, False if already present."""
    data = _load_deps(snapshot_dir)
    entry = data.setdefault(snapshot, {"depends_on": [], "note": None})
    if depends_on in entry["depends_on"]:
        return False
    entry["depends_on"].append(depends_on)
    if note is not None:
        entry["note"] = note
    _save_deps(snapshot_dir, data)
    return True


def remove_dependency(
    snapshot_dir: Path, snapshot: str, depends_on: str
) -> bool:
    data = _load_deps(snapshot_dir)
    entry = data.get(snapshot)
    if not entry or depends_on not in entry["depends_on"]:
        return False
    entry["depends_on"].remove(depends_on)
    _save_deps(snapshot_dir, data)
    return True


def get_report(snapshot_dir: Path) -> DependencyReport:
    data = _load_deps(snapshot_dir)
    entries = {
        name: DependencyEntry(
            snapshot=name,
            depends_on=raw.get("depends_on", []),
            note=raw.get("note"),
        )
        for name, raw in data.items()
    }
    return DependencyReport(entries=entries)
