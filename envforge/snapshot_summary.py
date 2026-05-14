"""Generate a human-readable summary report for a snapshot."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envforge.snapshot import load
from envforge.snapshot_stats import compute_stats
from envforge.lint import lint_snapshot
from envforge.lock import is_locked
from envforge.annotate import get_annotation


@dataclass
class SnapshotSummary:
    name: str
    total_keys: int
    empty_values: int
    avg_key_length: float
    avg_value_length: float
    lint_errors: int
    lint_warnings: int
    is_locked: bool
    annotation: Optional[str]
    sample_keys: list[str] = field(default_factory=list)


def summarize(snapshot_dir: Path, name: str) -> SnapshotSummary:
    """Build a SnapshotSummary for the given snapshot name."""
    env = load(snapshot_dir, name)

    stats = compute_stats(snapshot_dir, name)
    lint_report = lint_snapshot(snapshot_dir, name)
    locked = is_locked(snapshot_dir, name)
    note = get_annotation(snapshot_dir, name)

    errors = sum(1 for i in lint_report.issues if i.severity == "error")
    warnings = sum(1 for i in lint_report.issues if i.severity == "warning")

    sample = sorted(env.keys())[:5]

    return SnapshotSummary(
        name=name,
        total_keys=stats.total_keys,
        empty_values=stats.empty_count,
        avg_key_length=stats.avg_key_length,
        avg_value_length=stats.avg_value_length,
        lint_errors=errors,
        lint_warnings=warnings,
        is_locked=locked,
        annotation=note,
        sample_keys=sample,
    )


def format_summary(s: SnapshotSummary) -> str:
    """Return a formatted multi-line string describing the snapshot."""
    lines = [
        f"Snapshot : {s.name}",
        f"Keys     : {s.total_keys} (empty values: {s.empty_values})",
        f"Avg key len  : {s.avg_key_length:.1f}  |  Avg val len: {s.avg_value_length:.1f}",
        f"Lint     : {s.lint_errors} error(s), {s.lint_warnings} warning(s)",
        f"Locked   : {'yes' if s.is_locked else 'no'}",
        f"Note     : {s.annotation or '(none)'}",
    ]
    if s.sample_keys:
        lines.append("Sample keys: " + ", ".join(s.sample_keys))
    return "\n".join(lines)
