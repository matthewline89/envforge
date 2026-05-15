"""Snapshot retention policy management."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class RetentionPolicy:
    max_count: Optional[int] = None
    max_age_days: Optional[int] = None


@dataclass
class RetentionResult:
    snapshot: str
    policy: RetentionPolicy
    violates_count: bool = False
    violates_age: bool = False

    @property
    def compliant(self) -> bool:
        return not self.violates_count and not self.violates_age

    @property
    def status(self) -> str:
        if self.compliant:
            return "compliant"
        reasons = []
        if self.violates_count:
            reasons.append("exceeds max count")
        if self.violates_age:
            reasons.append("exceeds max age")
        return ", ".join(reasons)


def _retention_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "retention.json"


def _load_retention(snapshot_dir: Path) -> dict:
    p = _retention_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_retention(snapshot_dir: Path, data: dict) -> None:
    _retention_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def set_retention(snapshot_dir: Path, name: str, policy: RetentionPolicy) -> bool:
    """Attach a retention policy to a snapshot. Returns True if new."""
    data = _load_retention(snapshot_dir)
    is_new = name not in data
    data[name] = {
        "max_count": policy.max_count,
        "max_age_days": policy.max_age_days,
    }
    _save_retention(snapshot_dir, data)
    return is_new


def get_retention(snapshot_dir: Path, name: str) -> Optional[RetentionPolicy]:
    """Return the retention policy for a snapshot, or None."""
    data = _load_retention(snapshot_dir)
    entry = data.get(name)
    if entry is None:
        return None
    return RetentionPolicy(
        max_count=entry.get("max_count"),
        max_age_days=entry.get("max_age_days"),
    )


def remove_retention(snapshot_dir: Path, name: str) -> bool:
    """Remove retention policy. Returns True if it existed."""
    data = _load_retention(snapshot_dir)
    if name not in data:
        return False
    del data[name]
    _save_retention(snapshot_dir, data)
    return True


def list_retention(snapshot_dir: Path) -> dict[str, RetentionPolicy]:
    """Return all retention policies keyed by snapshot name."""
    data = _load_retention(snapshot_dir)
    return {
        name: RetentionPolicy(
            max_count=entry.get("max_count"),
            max_age_days=entry.get("max_age_days"),
        )
        for name, entry in data.items()
    }
