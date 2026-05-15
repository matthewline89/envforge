"""Checksum tracking for snapshots — detect unexpected mutations."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from envforge.snapshot import load


@dataclass
class ChecksumEntry:
    name: str
    checksum: str
    algorithm: str = "sha256"


@dataclass
class ChecksumVerifyResult:
    name: str
    expected: str
    actual: str
    algorithm: str

    @property
    def ok(self) -> bool:
        return self.expected == self.actual


def _checksums_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "checksums.json"


def _load_checksums(snapshot_dir: Path) -> dict:
    path = _checksums_path(snapshot_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_checksums(snapshot_dir: Path, data: dict) -> None:
    _checksums_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def _compute_checksum(env: dict, algorithm: str = "sha256") -> str:
    canonical = json.dumps(env, sort_keys=True, separators=(",", ":"))
    h = hashlib.new(algorithm)
    h.update(canonical.encode())
    return h.hexdigest()


def record_checksum(
    name: str,
    snapshot_dir: Path,
    algorithm: str = "sha256",
) -> ChecksumEntry:
    env = load(name, snapshot_dir)
    checksum = _compute_checksum(env, algorithm)
    data = _load_checksums(snapshot_dir)
    data[name] = {"checksum": checksum, "algorithm": algorithm}
    _save_checksums(snapshot_dir, data)
    return ChecksumEntry(name=name, checksum=checksum, algorithm=algorithm)


def verify_checksum(
    name: str,
    snapshot_dir: Path,
) -> Optional[ChecksumVerifyResult]:
    data = _load_checksums(snapshot_dir)
    if name not in data:
        return None
    entry = data[name]
    algorithm = entry.get("algorithm", "sha256")
    env = load(name, snapshot_dir)
    actual = _compute_checksum(env, algorithm)
    return ChecksumVerifyResult(
        name=name,
        expected=entry["checksum"],
        actual=actual,
        algorithm=algorithm,
    )


def remove_checksum(name: str, snapshot_dir: Path) -> bool:
    data = _load_checksums(snapshot_dir)
    if name not in data:
        return False
    del data[name]
    _save_checksums(snapshot_dir, data)
    return True


def list_checksums(snapshot_dir: Path) -> list[ChecksumEntry]:
    data = _load_checksums(snapshot_dir)
    return [
        ChecksumEntry(name=k, checksum=v["checksum"], algorithm=v.get("algorithm", "sha256"))
        for k, v in data.items()
    ]
