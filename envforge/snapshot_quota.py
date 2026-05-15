"""Snapshot quota management: enforce limits on snapshot count per directory."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_QUOTA_FILE = ".quota.json"


def _quota_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _QUOTA_FILE


def _load_quota(snapshot_dir: Path) -> dict:
    p = _quota_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_quota(snapshot_dir: Path, data: dict) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    _quota_path(snapshot_dir).write_text(json.dumps(data, indent=2))


@dataclass
class QuotaResult:
    limit: int
    current: int
    exceeded: bool
    headroom: int


def set_quota(snapshot_dir: Path, limit: int) -> None:
    """Persist a maximum snapshot count for *snapshot_dir*."""
    if limit < 1:
        raise ValueError("Quota limit must be at least 1.")
    data = _load_quota(snapshot_dir)
    data["limit"] = limit
    _save_quota(snapshot_dir, data)


def get_quota(snapshot_dir: Path) -> Optional[int]:
    """Return the configured limit, or *None* if no quota is set."""
    return _load_quota(snapshot_dir).get("limit")


def remove_quota(snapshot_dir: Path) -> bool:
    """Remove the quota for *snapshot_dir*. Returns True if one existed."""
    data = _load_quota(snapshot_dir)
    if "limit" not in data:
        return False
    del data["limit"]
    _save_quota(snapshot_dir, data)
    return True


def check_quota(snapshot_dir: Path) -> QuotaResult:
    """Return a QuotaResult describing the current usage vs. the limit.

    Counts every ``*.json`` file that is not the quota file itself.
    """
    limit = get_quota(snapshot_dir)
    if limit is None:
        raise ValueError("No quota configured for this directory.")
    current = len(
        [
            p
            for p in snapshot_dir.glob("*.json")
            if p.name != _QUOTA_FILE
        ]
    )
    exceeded = current > limit
    headroom = max(0, limit - current)
    return QuotaResult(limit=limit, current=current, exceeded=exceeded, headroom=headroom)
