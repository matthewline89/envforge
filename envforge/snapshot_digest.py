"""Compute and compare content-based digests for snapshots."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from envforge.snapshot import load


@dataclass
class DigestInfo:
    name: str
    digest: str
    key_count: int


def _compute_digest(env: dict[str, str]) -> str:
    """Return a stable SHA-256 hex digest of the sorted env dict."""
    canonical = json.dumps(env, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def digest_snapshot(snapshot_dir: Path, name: str) -> DigestInfo:
    """Load a snapshot and return its DigestInfo."""
    env = load(snapshot_dir, name)
    return DigestInfo(
        name=name,
        digest=_compute_digest(env),
        key_count=len(env),
    )


def digests_match(snapshot_dir: Path, name_a: str, name_b: str) -> bool:
    """Return True when two snapshots have identical content digests."""
    a = digest_snapshot(snapshot_dir, name_a)
    b = digest_snapshot(snapshot_dir, name_b)
    return a.digest == b.digest


def find_duplicates(
    snapshot_dir: Path, names: Optional[list[str]] = None
) -> dict[str, list[str]]:
    """Group snapshot names that share the same content digest.

    Returns a mapping of digest -> [name, ...] for groups with >1 member.
    """
    if names is None:
        names = [p.stem for p in sorted(snapshot_dir.glob("*.json"))]

    groups: dict[str, list[str]] = {}
    for name in names:
        try:
            info = digest_snapshot(snapshot_dir, name)
        except FileNotFoundError:
            continue
        groups.setdefault(info.digest, []).append(name)

    return {d: ns for d, ns in groups.items() if len(ns) > 1}
