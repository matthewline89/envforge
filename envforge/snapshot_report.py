"""Generate a human-readable report for one or more snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envforge.snapshot import load
from envforge.snapshot_stats import compute_stats
from envforge.lint import lint_snapshot
from envforge.expire import get_expiry


@dataclass
class SnapshotReportEntry:
    name: str
    total_keys: int
    empty_values: int
    lint_errors: int
    lint_warnings: int
    expires_at: Optional[str]
    is_expired: bool


@dataclass
class SnapshotReport:
    entries: List[SnapshotReportEntry] = field(default_factory=list)

    @property
    def total_snapshots(self) -> int:
        return len(self.entries)

    @property
    def snapshots_with_errors(self) -> int:
        return sum(1 for e in self.entries if e.lint_errors > 0)

    @property
    def expired_count(self) -> int:
        return sum(1 for e in self.entries if e.is_expired)


def build_report(snapshot_dir, names: Optional[List[str]] = None) -> SnapshotReport:
    """Build a SnapshotReport for the given snapshot names (or all)."""
    import os

    if names is None:
        names = [
            f[:-5]
            for f in os.listdir(snapshot_dir)
            if f.endswith(".json") and not f.startswith("_")
        ]

    entries: List[SnapshotReportEntry] = []
    for name in sorted(names):
        try:
            env = load(name, snapshot_dir)
        except FileNotFoundError:
            continue

        stats = compute_stats(name, snapshot_dir)
        lint_report = lint_snapshot(name, snapshot_dir)
        expiry = get_expiry(name, snapshot_dir)

        expires_at = expiry.expires_at if expiry else None
        is_expired = (expiry.is_expired if expiry else False)

        entries.append(
            SnapshotReportEntry(
                name=name,
                total_keys=stats.total_keys,
                empty_values=stats.empty_count,
                lint_errors=len([i for i in lint_report.issues if i.severity == "error"]),
                lint_warnings=len([i for i in lint_report.issues if i.severity == "warning"]),
                expires_at=expires_at,
                is_expired=is_expired,
            )
        )

    return SnapshotReport(entries=entries)


def format_report(report: SnapshotReport) -> str:
    """Return a formatted text representation of the report."""
    lines = [
        f"Snapshot Report  ({report.total_snapshots} snapshots)",
        "-" * 60,
    ]
    for e in report.entries:
        status = "EXPIRED" if e.is_expired else ("ERR" if e.lint_errors else "OK")
        lines.append(
            f"  [{status:7s}] {e.name}  keys={e.total_keys}  "
            f"empty={e.empty_values}  errors={e.lint_errors}  "
            f"warnings={e.lint_warnings}"
            + (f"  expires={e.expires_at}" if e.expires_at else "")
        )
    lines.append("-" * 60)
    lines.append(
        f"  Total: {report.total_snapshots}  "
        f"With errors: {report.snapshots_with_errors}  "
        f"Expired: {report.expired_count}"
    )
    return "\n".join(lines)
