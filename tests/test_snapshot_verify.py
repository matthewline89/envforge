"""Tests for envforge.snapshot_verify."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_verify import verify_snapshot, verify_all, VerifyResult, VerifyIssue


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(directory: Path, name: str, env: dict) -> None:
    (directory / f"{name}.json").write_text(json.dumps(env))


def test_verify_returns_verify_result(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap", {"KEY": "val"})
    result = verify_snapshot("snap", snapshot_dir)
    assert isinstance(result, VerifyResult)


def test_verify_ok_for_clean_snapshot(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "clean", {"A": "1", "B": "2"})
    result = verify_snapshot("clean", snapshot_dir)
    assert result.ok
    assert result.status == "OK"
    assert result.issues == []


def test_verify_warns_on_empty_value(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "empty_val", {"KEY": ""})
    result = verify_snapshot("empty_val", snapshot_dir)
    assert result.status == "WARN"
    assert any(i.severity == "warning" for i in result.issues)


def test_verify_warns_on_empty_snapshot(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "empty", {})
    result = verify_snapshot("empty", snapshot_dir)
    assert result.status == "WARN"
    assert any("no variables" in i.message for i in result.issues)


def test_verify_error_on_missing_file(snapshot_dir: Path) -> None:
    result = verify_snapshot("missing", snapshot_dir)
    assert not result.ok
    assert result.status == "FAIL"
    assert any(i.severity == "error" for i in result.issues)


def test_verify_error_on_invalid_json(snapshot_dir: Path) -> None:
    (snapshot_dir / "bad.json").write_text("not json")
    result = verify_snapshot("bad", snapshot_dir)
    assert not result.ok


def test_verify_digest_is_populated(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "snap", {"X": "y"})
    result = verify_snapshot("snap", snapshot_dir)
    assert result.digest.digest
    assert result.digest.snapshot == "snap"


def test_verify_all_returns_list(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "a", {"K": "v"})
    _write(snapshot_dir, "b", {"K": "v"})
    results = verify_all(snapshot_dir)
    assert len(results) == 2


def test_verify_all_empty_dir(snapshot_dir: Path) -> None:
    results = verify_all(snapshot_dir)
    assert results == []


def test_verify_all_includes_failed(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "good", {"A": "1"})
    (snapshot_dir / "bad.json").write_text("!!!")
    results = verify_all(snapshot_dir)
    statuses = {r.snapshot: r.status for r in results}
    assert statuses["good"] == "OK"
    assert statuses["bad"] == "FAIL"
