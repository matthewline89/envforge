"""Tests for envforge.lint."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.lint import LintIssue, LintReport, lint_dict, lint_snapshot


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


# --- lint_dict ---

def test_lint_dict_clean_env_returns_empty_report():
    report = lint_dict("prod", {"HOST": "localhost", "PORT": "8080"})
    assert report.is_clean
    assert report.snapshot_name == "prod"


def test_lint_dict_detects_empty_value():
    report = lint_dict("prod", {"HOST": ""})
    assert not report.is_clean
    issue = report.issues[0]
    assert issue.key == "HOST"
    assert issue.severity == "warning"
    assert "empty" in issue.message.lower()


def test_lint_dict_detects_suspicious_key():
    report = lint_dict("prod", {"DB_PASSWORD": "s3cr3t"})
    keys_flagged = [i.key for i in report.issues]
    assert "DB_PASSWORD" in keys_flagged
    severities = {i.key: i.severity for i in report.issues}
    assert severities["DB_PASSWORD"] == "warning"


def test_lint_dict_detects_token_in_key():
    report = lint_dict("ci", {"GITHUB_TOKEN": "abc123"})
    assert any(i.key == "GITHUB_TOKEN" for i in report.issues)


def test_lint_dict_detects_duplicate_values():
    report = lint_dict("dev", {"A": "same", "B": "same"})
    keys = [i.key for i in report.issues]
    assert "B" in keys


def test_lint_dict_no_duplicate_flag_for_empty_values():
    """Empty values should not trigger duplicate detection."""
    report = lint_dict("dev", {"A": "", "B": ""})
    duplicate_issues = [
        i for i in report.issues if "identical" in i.message
    ]
    assert len(duplicate_issues) == 0


def test_lint_dict_detects_key_with_spaces():
    report = lint_dict("bad", {"MY KEY": "value"})
    error_issues = [i for i in report.issues if i.severity == "error"]
    assert len(error_issues) == 1
    assert error_issues[0].key == "MY KEY"


def test_lint_report_has_errors_property():
    report = LintReport(snapshot_name="x", issues=[
        LintIssue(key="K", message="bad", severity="error")
    ])
    assert report.has_errors
    assert not report.is_clean


def test_lint_report_has_warnings_property():
    report = LintReport(snapshot_name="x", issues=[
        LintIssue(key="K", message="warn", severity="warning")
    ])
    assert report.has_warnings
    assert not report.has_errors


# --- lint_snapshot ---

def test_lint_snapshot_loads_and_lints(snapshot_dir: Path):
    _write(snapshot_dir, "mysnap", {"API_KEY": "topsecret", "PORT": "3000"})
    report = lint_snapshot("mysnap", snapshot_dir)
    assert report.snapshot_name == "mysnap"
    flagged = [i.key for i in report.issues]
    assert "API_KEY" in flagged


def test_lint_snapshot_clean(snapshot_dir: Path):
    _write(snapshot_dir, "clean", {"HOST": "example.com", "PORT": "443"})
    report = lint_snapshot("clean", snapshot_dir)
    assert report.is_clean
