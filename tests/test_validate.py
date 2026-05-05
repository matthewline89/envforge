"""Tests for envforge.validate."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.validate import (
    ValidationError,
    ValidationReport,
    validate_dict,
    validate_snapshot,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envforge"
    d.mkdir()
    return d


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


# --- validate_dict ---

def test_clean_env_is_valid():
    report = validate_dict({"FOO": "bar", "BAZ": "qux"}, "snap")
    assert report.is_valid
    assert not report.errors


def test_empty_value_produces_warning():
    report = validate_dict({"FOO": ""}, "snap")
    assert report.is_valid  # warnings don't fail
    assert report.has_warnings
    assert any(e.key == "FOO" and e.severity == "warning" for e in report.errors)


def test_key_with_space_produces_error():
    report = validate_dict({"BAD KEY": "val"}, "snap")
    assert not report.is_valid
    assert any("whitespace" in e.message for e in report.errors)


def test_required_key_missing_produces_error():
    report = validate_dict({"FOO": "bar"}, "snap", required_keys=["MISSING"])
    assert not report.is_valid
    assert any(e.key == "MISSING" for e in report.errors)


def test_required_key_present_is_ok():
    report = validate_dict({"FOO": "bar"}, "snap", required_keys=["FOO"])
    assert report.is_valid


def test_forbidden_key_present_produces_error():
    report = validate_dict({"SECRET": "val"}, "snap", forbidden_keys=["SECRET"])
    assert not report.is_valid
    assert any(e.key == "SECRET" for e in report.errors)


def test_forbidden_key_absent_is_ok():
    report = validate_dict({"FOO": "bar"}, "snap", forbidden_keys=["SECRET"])
    assert report.is_valid


def test_key_pattern_match_is_ok():
    report = validate_dict({"FOO_BAR": "val"}, "snap", key_pattern=r"^[A-Z_]+$")
    assert report.is_valid


def test_key_pattern_mismatch_produces_error():
    report = validate_dict({"foo_bar": "val"}, "snap", key_pattern=r"^[A-Z_]+$")
    assert not report.is_valid
    assert any("pattern" in e.message for e in report.errors)


# --- summary ---

def test_summary_ok_when_no_errors():
    report = ValidationReport(snapshot_name="mysnap")
    assert "OK" in report.summary()


def test_summary_lists_issues():
    report = ValidationReport(
        snapshot_name="mysnap",
        errors=[ValidationError(key="FOO", message="Required key is missing")],
    )
    assert "FOO" in report.summary()
    assert "Required key is missing" in report.summary()


# --- validate_snapshot ---

def test_validate_snapshot_loads_and_validates(snapshot_dir):
    _write(snapshot_dir, "prod", {"DATABASE_URL": "postgres://localhost/db"})
    report = validate_snapshot(snapshot_dir, "prod", required_keys=["DATABASE_URL"])
    assert report.is_valid


def test_validate_snapshot_raises_for_missing(snapshot_dir):
    with pytest.raises(FileNotFoundError):
        validate_snapshot(snapshot_dir, "nonexistent")
