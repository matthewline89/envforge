"""Verify snapshot integrity by checking digests and structure."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envforge.snapshot import load
from envforge.snapshot_digest import digest_snapshot, DigestInfo


@dataclass
class VerifyIssue:
    snapshot: str
    message: str
    severity: str  # "error" | "warning"


@dataclass
class VerifyResult:
    snapshot: str
    digest: DigestInfo
    issues: List[VerifyIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def status(self) -> str:
        if any(i.severity == "error" for i in self.issues):
            return "FAIL"
        if any(i.severity == "warning" for i in self.issues):
            return "WARN"
        return "OK"


def verify_snapshot(name: str, snapshot_dir: Path) -> VerifyResult:
    """Load a snapshot and run structural integrity checks."""
    info = digest_snapshot(name, snapshot_dir)
    issues: List[VerifyIssue] = []

    try:
        env = load(name, snapshot_dir)
    except Exception as exc:  # noqa: BLE001
        issues.append(VerifyIssue(name, f"Cannot load snapshot: {exc}", "error"))
        return VerifyResult(snapshot=name, digest=info, issues=issues)

    if not isinstance(env, dict):
        issues.append(VerifyIssue(name, "Snapshot root is not a dict", "error"))
        return VerifyResult(snapshot=name, digest=info, issues=issues)

    for key, value in env.items():
        if not isinstance(key, str):
            issues.append(VerifyIssue(name, f"Non-string key: {key!r}", "error"))
        if not isinstance(value, str):
            issues.append(VerifyIssue(name, f"Non-string value for key {key!r}", "error"))
        elif value == "":
            issues.append(VerifyIssue(name, f"Empty value for key {key!r}", "warning"))

    if not env:
        issues.append(VerifyIssue(name, "Snapshot contains no variables", "warning"))

    return VerifyResult(snapshot=name, digest=info, issues=issues)


def verify_all(snapshot_dir: Path) -> List[VerifyResult]:
    """Verify every snapshot in *snapshot_dir*."""
    results = []
    for path in sorted(snapshot_dir.glob("*.json")):
        name = path.stem
        results.append(verify_snapshot(name, snapshot_dir))
    return results
