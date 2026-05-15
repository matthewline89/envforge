"""Tests for envforge.snapshot_cleanup."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_cleanup import cleanup_orphans, total_removed, CleanupResult


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write_snapshot(d: Path, name: str, env: dict | None = None) -> None:
    (d / f"{name}.json").write_text(json.dumps(env or {"KEY": "val"}))


def _write_meta(d: Path, filename: str, data: dict) -> None:
    (d / filename).write_text(json.dumps(data))


def test_cleanup_result_defaults_empty():
    r = CleanupResult()
    assert r.removed_snapshots == []
    assert r.pruned_metadata_keys == []


def test_total_removed_sums_both_lists():
    r = CleanupResult(removed_snapshots=["a"], pruned_metadata_keys=["b", "c"])
    assert total_removed(r) == 3


def test_no_orphans_returns_empty_result(snapshot_dir):
    _write_snapshot(snapshot_dir, "prod")
    _write_meta(snapshot_dir, "tags.json", {"prod": "release"})
    result = cleanup_orphans(snapshot_dir)
    assert result.pruned_metadata_keys == []


def test_orphan_key_detected(snapshot_dir):
    _write_snapshot(snapshot_dir, "prod")
    _write_meta(snapshot_dir, "tags.json", {"prod": "release", "ghost": "old"})
    result = cleanup_orphans(snapshot_dir)
    assert any("ghost" in k for k in result.pruned_metadata_keys)


def test_orphan_key_removed_from_file(snapshot_dir):
    _write_snapshot(snapshot_dir, "prod")
    _write_meta(snapshot_dir, "tags.json", {"prod": "release", "ghost": "old"})
    cleanup_orphans(snapshot_dir)
    data = json.loads((snapshot_dir / "tags.json").read_text())
    assert "ghost" not in data
    assert "prod" in data


def test_dry_run_does_not_modify_file(snapshot_dir):
    _write_snapshot(snapshot_dir, "prod")
    _write_meta(snapshot_dir, "tags.json", {"prod": "release", "ghost": "old"})
    cleanup_orphans(snapshot_dir, dry_run=True)
    data = json.loads((snapshot_dir / "tags.json").read_text())
    assert "ghost" in data


def test_dry_run_still_reports_orphans(snapshot_dir):
    _write_snapshot(snapshot_dir, "prod")
    _write_meta(snapshot_dir, "tags.json", {"prod": "release", "ghost": "old"})
    result = cleanup_orphans(snapshot_dir, dry_run=True)
    assert any("ghost" in k for k in result.pruned_metadata_keys)


def test_missing_metadata_file_skipped(snapshot_dir):
    _write_snapshot(snapshot_dir, "prod")
    result = cleanup_orphans(snapshot_dir)
    assert total_removed(result) == 0


def test_multiple_metadata_files_cleaned(snapshot_dir):
    _write_snapshot(snapshot_dir, "prod")
    _write_meta(snapshot_dir, "tags.json", {"ghost": "x"})
    _write_meta(snapshot_dir, "aliases.json", {"specter": "y"})
    result = cleanup_orphans(snapshot_dir)
    assert len(result.pruned_metadata_keys) == 2
