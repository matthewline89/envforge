"""Tests for envforge.snapshot_score."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_score import score_snapshot, SnapshotScore, ScoreBreakdown


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


def test_score_returns_snapshot_score(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "mysnap", {"HOME": "/root", "PATH": "/usr/bin"})
    result = score_snapshot("mysnap", snapshot_dir)
    assert isinstance(result, SnapshotScore)


def test_score_name_matches(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "mysnap", {"HOME": "/root"})
    result = score_snapshot("mysnap", snapshot_dir)
    assert result.name == "mysnap"


def test_score_has_breakdown(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "mysnap", {"HOME": "/root"})
    result = score_snapshot("mysnap", snapshot_dir)
    assert isinstance(result.breakdown, ScoreBreakdown)


def test_grade_a_for_clean_env(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "clean", {"MY_VAR": "hello", "ANOTHER_KEY": "world"})
    result = score_snapshot("clean", snapshot_dir)
    assert result.grade in ("A", "B")


def test_empty_value_reduces_score(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "empty_val", {"MY_VAR": ""})
    result = score_snapshot("empty_val", snapshot_dir)
    assert result.breakdown.empty_value_penalty >= 1


def test_lowercase_key_reduces_score(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "lowercase", {"my_var": "value"})
    result = score_snapshot("lowercase", snapshot_dir)
    assert result.breakdown.suspicious_key_penalty >= 1


def test_score_never_negative(snapshot_dir: Path) -> None:
    env = {"a": "", "b": "", "c": "", "d": "", "e": "", "f": ""}
    _write(snapshot_dir, "bad", env)
    result = score_snapshot("bad", snapshot_dir)
    assert result.score >= 0


def test_percent_is_float(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "pct", {"KEY": "val"})
    result = score_snapshot("pct", snapshot_dir)
    assert isinstance(result.percent, float)


def test_well_named_key_adds_bonus(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "good", {"MY_GREAT_VAR": "value"})
    result = score_snapshot("good", snapshot_dir)
    assert result.breakdown.bonus_well_named >= 1


def test_max_score_scales_with_key_count(snapshot_dir: Path) -> None:
    small = {"A": "1"}
    large = {f"KEY_{i}": str(i) for i in range(10)}
    _write(snapshot_dir, "small", small)
    _write(snapshot_dir, "large", large)
    r_small = score_snapshot("small", snapshot_dir)
    r_large = score_snapshot("large", snapshot_dir)
    assert r_large.max_score > r_small.max_score
