"""Tests for envforge.snapshot_mirror."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_mirror import MirrorError, MirrorResult, mirror_snapshots


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(directory: Path, name: str, env: dict) -> Path:
    p = directory / f"{name}.json"
    p.write_text(json.dumps(env))
    return p


def test_mirror_result_total_copied() -> None:
    r = MirrorResult(source="a", destination="b", copied=["x", "y"])
    assert r.total_copied == 2


def test_mirror_result_total_skipped() -> None:
    r = MirrorResult(source="a", destination="b", skipped=["z"])
    assert r.total_skipped == 1


def test_mirror_raises_when_source_missing(snapshot_dir: Path) -> None:
    with pytest.raises(MirrorError, match="Source directory does not exist"):
        mirror_snapshots(snapshot_dir / "no_such_dir", snapshot_dir / "dest")


def test_mirror_creates_destination_directory(snapshot_dir: Path) -> None:
    src = snapshot_dir / "src"
    src.mkdir()
    _write(src, "snap1", {"A": "1"})
    dst = snapshot_dir / "dst"

    mirror_snapshots(src, dst)

    assert dst.is_dir()


def test_mirror_copies_all_snapshots(snapshot_dir: Path) -> None:
    src = snapshot_dir / "src"
    src.mkdir()
    _write(src, "snap1", {"A": "1"})
    _write(src, "snap2", {"B": "2"})
    dst = snapshot_dir / "dst"

    result = mirror_snapshots(src, dst)

    assert set(result.copied) == {"snap1", "snap2"}
    assert (dst / "snap1.json").exists()
    assert (dst / "snap2.json").exists()


def test_mirror_skips_existing_by_default(snapshot_dir: Path) -> None:
    src = snapshot_dir / "src"
    src.mkdir()
    _write(src, "snap1", {"A": "1"})
    dst = snapshot_dir / "dst"
    dst.mkdir()
    _write(dst, "snap1", {"A": "old"})

    result = mirror_snapshots(src, dst)

    assert "snap1" in result.skipped
    assert result.total_copied == 0
    # Original content preserved
    assert json.loads((dst / "snap1.json").read_text()) == {"A": "old"}


def test_mirror_overwrites_when_flag_set(snapshot_dir: Path) -> None:
    src = snapshot_dir / "src"
    src.mkdir()
    _write(src, "snap1", {"A": "new"})
    dst = snapshot_dir / "dst"
    dst.mkdir()
    _write(dst, "snap1", {"A": "old"})

    result = mirror_snapshots(src, dst, overwrite=True)

    assert "snap1" in result.overwritten
    assert json.loads((dst / "snap1.json").read_text()) == {"A": "new"}


def test_mirror_filters_by_name(snapshot_dir: Path) -> None:
    src = snapshot_dir / "src"
    src.mkdir()
    _write(src, "snap1", {"A": "1"})
    _write(src, "snap2", {"B": "2"})
    dst = snapshot_dir / "dst"

    result = mirror_snapshots(src, dst, names=["snap1"])

    assert result.copied == ["snap1"]
    assert not (dst / "snap2.json").exists()


def test_mirror_returns_mirror_result_type(snapshot_dir: Path) -> None:
    src = snapshot_dir / "src"
    src.mkdir()
    dst = snapshot_dir / "dst"

    result = mirror_snapshots(src, dst)

    assert isinstance(result, MirrorResult)
    assert result.source == str(src)
    assert result.destination == str(dst)
