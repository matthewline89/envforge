"""Tests for envforge.snapshot_copy."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_copy import CopyError, CopyResult, copy_keys


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(directory: Path, name: str, env: dict) -> None:
    (directory / f"{name}.json").write_text(json.dumps(env))


# ---------------------------------------------------------------------------
# CopyResult helpers
# ---------------------------------------------------------------------------

def test_copy_result_total_copied() -> None:
    r = CopyResult(source="a", destination="b", keys_copied=["X", "Y"])
    assert r.total_copied == 2


def test_copy_result_total_skipped() -> None:
    r = CopyResult(source="a", destination="b", keys_skipped=["Z"])
    assert r.total_skipped == 1


# ---------------------------------------------------------------------------
# copy_keys — happy paths
# ---------------------------------------------------------------------------

def test_copy_all_keys_creates_destination(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "src", {"A": "1", "B": "2"})
    result = copy_keys("src", "dst", keys=None, overwrite=True, snapshot_dir=str(snapshot_dir))
    dst_path = snapshot_dir / "dst.json"
    assert dst_path.exists()
    assert result.total_copied == 2


def test_copy_specific_keys(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "src", {"A": "1", "B": "2", "C": "3"})
    result = copy_keys("src", "dst", keys=["A", "C"], overwrite=True, snapshot_dir=str(snapshot_dir))
    assert result.keys_copied == ["A", "C"]
    assert result.total_skipped == 0


def test_copy_merges_into_existing_destination(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "src", {"NEW": "hello"})
    _write(snapshot_dir, "dst", {"OLD": "world"})
    copy_keys("src", "dst", keys=None, overwrite=True, snapshot_dir=str(snapshot_dir))
    data = json.loads((snapshot_dir / "dst.json").read_text())
    assert data["OLD"] == "world"
    assert data["NEW"] == "hello"


def test_copy_overwrites_existing_key_when_flag_set(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "src", {"K": "new_val"})
    _write(snapshot_dir, "dst", {"K": "old_val"})
    copy_keys("src", "dst", keys=None, overwrite=True, snapshot_dir=str(snapshot_dir))
    data = json.loads((snapshot_dir / "dst.json").read_text())
    assert data["K"] == "new_val"


def test_copy_skips_existing_key_when_no_overwrite(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "src", {"K": "new_val"})
    _write(snapshot_dir, "dst", {"K": "old_val"})
    result = copy_keys("src", "dst", keys=None, overwrite=False, snapshot_dir=str(snapshot_dir))
    assert "K" in result.keys_skipped
    data = json.loads((snapshot_dir / "dst.json").read_text())
    assert data["K"] == "old_val"


def test_copy_skips_missing_key_in_source(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "src", {"A": "1"})
    result = copy_keys("src", "dst", keys=["A", "MISSING"], overwrite=True, snapshot_dir=str(snapshot_dir))
    assert "MISSING" in result.keys_skipped
    assert "A" in result.keys_copied


# ---------------------------------------------------------------------------
# copy_keys — error paths
# ---------------------------------------------------------------------------

def test_copy_raises_when_source_missing(snapshot_dir: Path) -> None:
    with pytest.raises(CopyError, match="ghost"):
        copy_keys("ghost", "dst", keys=None, overwrite=True, snapshot_dir=str(snapshot_dir))


def test_copy_result_source_and_destination_stored(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "alpha", {"X": "1"})
    result = copy_keys("alpha", "beta", keys=None, overwrite=True, snapshot_dir=str(snapshot_dir))
    assert result.source == "alpha"
    assert result.destination == "beta"
