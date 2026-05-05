"""Tests for envforge.rename."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.rename import RenameError, rename_snapshot


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _write(directory: Path, name: str, data: dict) -> Path:
    p = directory / f"{name}.json"
    p.write_text(json.dumps(data))
    return p


def test_rename_moves_file(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "old", {"KEY": "val"})
    dest = rename_snapshot(snapshot_dir, "old", "new")
    assert dest == snapshot_dir / "new.json"
    assert dest.exists()
    assert not (snapshot_dir / "old.json").exists()


def test_rename_raises_when_source_missing(snapshot_dir: Path) -> None:
    with pytest.raises(RenameError, match="does not exist"):
        rename_snapshot(snapshot_dir, "ghost", "new")


def test_rename_raises_when_dest_exists(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "old", {"A": "1"})
    _write(snapshot_dir, "new", {"B": "2"})
    with pytest.raises(RenameError, match="already exists"):
        rename_snapshot(snapshot_dir, "old", "new")


def test_rename_migrates_tags(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "old", {})
    tags_path = snapshot_dir / "tags.json"
    tags_path.write_text(json.dumps({"v1": "old", "stable": "other"}))

    rename_snapshot(snapshot_dir, "old", "new")

    tags = json.loads(tags_path.read_text())
    assert tags["v1"] == "new"
    assert tags["stable"] == "other"


def test_rename_migrates_aliases(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "old", {})
    aliases_path = snapshot_dir / "aliases.json"
    aliases_path.write_text(json.dumps({"prod": "old"}))

    rename_snapshot(snapshot_dir, "old", "new")

    aliases = json.loads(aliases_path.read_text())
    assert aliases["prod"] == "new"


def test_rename_skips_tags_migration_when_disabled(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "old", {})
    tags_path = snapshot_dir / "tags.json"
    tags_path.write_text(json.dumps({"v1": "old"}))

    rename_snapshot(snapshot_dir, "old", "new", migrate_tags=False)

    tags = json.loads(tags_path.read_text())
    assert tags["v1"] == "old"  # unchanged


def test_rename_skips_aliases_migration_when_disabled(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "old", {})
    aliases_path = snapshot_dir / "aliases.json"
    aliases_path.write_text(json.dumps({"prod": "old"}))

    rename_snapshot(snapshot_dir, "old", "new", migrate_aliases=False)

    aliases = json.loads(aliases_path.read_text())
    assert aliases["prod"] == "old"  # unchanged


def test_rename_tolerates_missing_tags_file(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "old", {})
    # No tags.json present — should not raise
    rename_snapshot(snapshot_dir, "old", "new")
    assert (snapshot_dir / "new.json").exists()
