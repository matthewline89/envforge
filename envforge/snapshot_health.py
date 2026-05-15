"""Snapshot health check: aggregates lint, expiry, lock, and freeze status."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envforge.lint import lint_snapshot, LintReport
from envforge.expire import is_expired
from envforge.lock import is_locked
from envforge.snapshot_freeze import is_frozen


@dataclass
class HealthReport:
    name: str
    lint: LintReport
    expired: bool
    locked: bool
    frozen: bool
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.expired:
            self.warnings.append("snapshot is past its expiry date")
        if self.lint.has_errors():
            for issue in self.lint.issues:
                if issue.severity == "error":
                    self.errors.append(issue.message)
        if self.lint.has_warnings():
            for issue in self.lint.issues:
                if issue.severity == "warning":
                    self.warnings.append(issue.message)

    @property
    def healthy(self) -> bool:
        return not self.errors and not self.expired

    @property
    def status(self) -> str:
        if self.errors:
            return "error"
        if self.expired:
            return "expired"
        if self.warnings:
            return "warning"
        return "ok"


def check_health(name: str, snapshot_dir: Path) -> HealthReport:
    """Run all health checks for *name* and return a HealthReport."""
    lint = lint_snapshot(name, snapshot_dir)
    expired = is_expired(name, snapshot_dir)
    locked = is_locked(name, snapshot_dir)
    frozen = is_frozen(name, snapshot_dir)
    return HealthReport(
        name=name,
        lint=lint,
        expired=expired,
        locked=locked,
        frozen=frozen,
    )
