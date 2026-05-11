"""Compute a quality score for a snapshot based on various heuristics."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envforge.snapshot import load
from envforge.lint import lint_dict


@dataclass
class ScoreBreakdown:
    total_keys: int = 0
    empty_value_penalty: int = 0
    suspicious_key_penalty: int = 0
    lint_error_penalty: int = 0
    lint_warning_penalty: int = 0
    bonus_well_named: int = 0
    details: List[str] = field(default_factory=list)


@dataclass
class SnapshotScore:
    name: str
    score: int
    max_score: int
    breakdown: ScoreBreakdown

    @property
    def grade(self) -> str:
        ratio = self.score / self.max_score if self.max_score else 0
        if ratio >= 0.9:
            return "A"
        if ratio >= 0.75:
            return "B"
        if ratio >= 0.55:
            return "C"
        if ratio >= 0.35:
            return "D"
        return "F"

    @property
    def percent(self) -> float:
        return round(100 * self.score / self.max_score, 1) if self.max_score else 0.0


def score_snapshot(name: str, snapshot_dir: Path) -> SnapshotScore:
    """Score a snapshot and return a SnapshotScore."""
    env: Dict[str, str] = load(name, snapshot_dir)
    report = lint_dict(env)
    bd = ScoreBreakdown()
    bd.total_keys = len(env)

    max_score = max(bd.total_keys * 10, 10)
    score = max_score

    for issue in report.issues:
        if issue.severity == "error":
            score -= 5
            bd.lint_error_penalty += 5
            bd.details.append(f"error: {issue.message}")
        elif issue.severity == "warning":
            score -= 2
            bd.lint_warning_penalty += 2
            bd.details.append(f"warning: {issue.message}")

    for key, value in env.items():
        if not value:
            score -= 1
            bd.empty_value_penalty += 1
        if key != key.upper():
            score -= 1
            bd.suspicious_key_penalty += 1
        elif "_" in key and len(key) > 3:
            score += 1
            bd.bonus_well_named += 1

    score = max(0, min(score, max_score))
    return SnapshotScore(name=name, score=score, max_score=max_score, breakdown=bd)
