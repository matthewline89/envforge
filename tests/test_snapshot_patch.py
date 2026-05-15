"""Tests for envforge.snapshot_patch."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.snapshot_patch import PatchError, PatchResult, patch_snapshot
from envforge.cli_snapshot_patch import patch_group


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


# --- unit tests ---

def test_patch_result_total_changes_empty():
    r = PatchResult(name="x")
    assert r.total_changes == 0


def test_patch_result_total_changes_counts_all():
    r = PatchResult(name="x", added=["A"], updated=["B", "C"], deleted=["D"])
    assert r.total_changes == 4


def test_patch_adds_new_key(snapshot_dir):
    _write(snapshot_dir, "dev", {"FOO": "bar"})
    result = patch_snapshot("dev", str(snapshot_dir), set_vars={"NEW": "val"})
    assert "NEW" in result.added
    assert "NEW" not in result.updated


def test_patch_updates_existing_key(snapshot_dir):
    _write(snapshot_dir, "dev", {"FOO": "bar"})
    result = patch_snapshot("dev", str(snapshot_dir), set_vars={"FOO": "baz"})
    assert "FOO" in result.updated
    assert "FOO" not in result.added


def test_patch_deletes_key(snapshot_dir):
    _write(snapshot_dir, "dev", {"FOO": "bar", "BAZ": "qux"})
    result = patch_snapshot("dev", str(snapshot_dir), delete_keys=["BAZ"])
    assert "BAZ" in result.deleted
    data = json.loads((snapshot_dir / "dev.json").read_text())
    assert "BAZ" not in data


def test_patch_ignores_missing_delete_key(snapshot_dir):
    _write(snapshot_dir, "dev", {"FOO": "bar"})
    result = patch_snapshot("dev", str(snapshot_dir), delete_keys=["MISSING"])
    assert "MISSING" not in result.deleted
    assert result.total_changes == 0


def test_patch_persists_changes(snapshot_dir):
    _write(snapshot_dir, "dev", {"A": "1"})
    patch_snapshot("dev", str(snapshot_dir), set_vars={"B": "2"}, delete_keys=["A"])
    data = json.loads((snapshot_dir / "dev.json").read_text())
    assert data == {"B": "2"}


def test_patch_raises_for_missing_snapshot(snapshot_dir):
    with pytest.raises(PatchError, match="not found"):
        patch_snapshot("ghost", str(snapshot_dir))


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_apply_cmd_prints_patched(runner, snap_dir):
    _write(snap_dir, "env", {"X": "1"})
    res = runner.invoke(patch_group, ["apply", "env", "-s", "Y=2", "--dir", str(snap_dir)])
    assert res.exit_code == 0
    assert "Patched snapshot 'env'" in res.output


def test_apply_cmd_reports_added(runner, snap_dir):
    _write(snap_dir, "env", {})
    res = runner.invoke(patch_group, ["apply", "env", "-s", "NEW=val", "--dir", str(snap_dir)])
    assert "Added" in res.output
    assert "NEW" in res.output


def test_apply_cmd_reports_no_changes(runner, snap_dir):
    _write(snap_dir, "env", {"X": "1"})
    res = runner.invoke(patch_group, ["apply", "env", "--dir", str(snap_dir)])
    assert "No changes applied" in res.output


def test_apply_cmd_fails_on_bad_set_format(runner, snap_dir):
    _write(snap_dir, "env", {})
    res = runner.invoke(patch_group, ["apply", "env", "-s", "NOEQUALS", "--dir", str(snap_dir)])
    assert res.exit_code != 0


def test_apply_cmd_fails_for_missing_snapshot(runner, snap_dir):
    res = runner.invoke(patch_group, ["apply", "ghost", "--dir", str(snap_dir)])
    assert res.exit_code != 0
    assert "not found" in res.output
