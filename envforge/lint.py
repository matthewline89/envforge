"""Lint snapshots for common issues like empty values, duplicates, or suspicious keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envforge.snapshot import load


@dataclass
class LintIssue:
    key: str
    message: str
    severity: str  # "warning" | "error"


@dataclass
class LintReport:
    snapshot_name: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    @property
    def is_clean(self) -> bool:
        return len(self.issues) == 0


_SUSPICIOUS_PATTERNS = ("password", "secret", "token", "api_key", "private")


def lint_dict(name: str, env: Dict[str, str]) -> LintReport:
    """Run lint checks against an env dict and return a LintReport."""
    report = LintReport(snapshot_name=name)

    seen_values: Dict[str, str] = {}

    for key, value in env.items():
        # Check for empty values
        if value == "":
            report.issues.append(
                LintIssue(key=key, message="Value is empty.", severity="warning")
            )

        # Check for suspicious plaintext secrets
        lower_key = key.lower()
        if any(pat in lower_key for pat in _SUSPICIOUS_PATTERNS):
            report.issues.append(
                LintIssue(
                    key=key,
                    message="Key name suggests a secret; consider encrypting this snapshot.",
                    severity="warning",
                )
            )

        # Check for duplicate values across different keys
        if value and value in seen_values:
            report.issues.append(
                LintIssue(
                    key=key,
                    message=f"Value is identical to key '{seen_values[value]}'.",
                    severity="warning",
                )
            )
        elif value:
            seen_values[value] = key

        # Check for keys containing spaces (invalid in most shells)
        if " " in key:
            report.issues.append(
                LintIssue(
                    key=key,
                    message="Key contains spaces, which is invalid in most shells.",
                    severity="error",
                )
            )

    return report


def lint_snapshot(name: str, snapshot_dir: Path) -> LintReport:
    """Load a snapshot by name and lint it."""
    env = load(name, snapshot_dir)
    return lint_dict(name, env)
