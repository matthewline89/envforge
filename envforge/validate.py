"""Validate snapshot contents against a schema or set of rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envforge.snapshot import load


@dataclass
class ValidationError:
    key: str
    message: str
    severity: str = "error"  # "error" | "warning"


@dataclass
class ValidationReport:
    snapshot_name: str
    errors: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not any(e.severity == "error" for e in self.errors)

    @property
    def has_warnings(self) -> bool:
        return any(e.severity == "warning" for e in self.errors)

    def summary(self) -> str:
        if not self.errors:
            return f"{self.snapshot_name}: OK"
        lines = [f"{self.snapshot_name}: {len(self.errors)} issue(s)"]
        for e in self.errors:
            lines.append(f"  [{e.severity.upper()}] {e.key}: {e.message}")
        return "\n".join(lines)


def validate_dict(
    env: Dict[str, str],
    snapshot_name: str,
    required_keys: Optional[List[str]] = None,
    forbidden_keys: Optional[List[str]] = None,
    key_pattern: Optional[str] = None,
) -> ValidationReport:
    """Validate an env dict against optional rules."""
    import re

    report = ValidationReport(snapshot_name=snapshot_name)

    for k, v in env.items():
        if not k:
            report.errors.append(ValidationError(key="(empty)", message="Key must not be empty"))
        if " " in k:
            report.errors.append(ValidationError(key=k, message="Key contains whitespace"))
        if key_pattern and not re.fullmatch(key_pattern, k):
            report.errors.append(
                ValidationError(key=k, message=f"Key does not match pattern '{key_pattern}'")
            )
        if v == "" :
            report.errors.append(
                ValidationError(key=k, message="Value is empty", severity="warning")
            )

    for rk in required_keys or []:
        if rk not in env:
            report.errors.append(ValidationError(key=rk, message="Required key is missing"))

    for fk in forbidden_keys or []:
        if fk in env:
            report.errors.append(
                ValidationError(key=fk, message="Forbidden key is present")
            )

    return report


def validate_snapshot(
    snapshot_dir: Path,
    name: str,
    required_keys: Optional[List[str]] = None,
    forbidden_keys: Optional[List[str]] = None,
    key_pattern: Optional[str] = None,
) -> ValidationReport:
    """Load a snapshot by name and validate it."""
    env = load(snapshot_dir, name)
    return validate_dict(
        env,
        snapshot_name=name,
        required_keys=required_keys,
        forbidden_keys=forbidden_keys,
        key_pattern=key_pattern,
    )
