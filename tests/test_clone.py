"""Tests for envforge.clone."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.clone import CloneError, clone_snapshot


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snaps"
    d.mkdir()
    return d


def _write(directory: Path, name: str, env: dict) -> Path:
    p = directory / f"{name}.json"
    p.write_text(json.dumps(env))
    return p


def test_clone_creates_destination_file(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "base", {"KEY": "val"})
    out = clone_snapshot("base", "copy", snapshot_dir)
    assert out.exists()
    assert out.name == "copy.json"


def test_clone_preserves_env_vars(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "base", {"FOO": "bar", "BAZ": "qux"})
    clone_snapshot("base", "copy", snapshot_dir)
    data = json.loads((snapshot_dir / "copy.json").read_text())
    assert data["FOO"] == "bar"
    assert data["BAZ"] == "qux"


def test_clone_raises_when_source_missing(snapshot_dir: Path) -> None:
    with pytest.raises(CloneError, match="does not exist"):
        clone_snapshot("ghost", "copy", snapshot_dir)


def test_clone_raises_when_dest_exists_without_overwrite(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "base", {"A": "1"})
    _write(snapshot_dir, "copy", {"B": "2"})
    with pytest.raises(CloneError, match="already exists"):
        clone_snapshot("base", "copy", snapshot_dir)


def test_clone_overwrites_when_flag_set(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "base", {"NEW": "val"})
    _write(snapshot_dir, "copy", {"OLD": "val"})
    clone_snapshot("base", "copy", snapshot_dir, overwrite=True)
    data = json.loads((snapshot_dir / "copy.json").read_text())
    assert "NEW" in data
    assert "OLD" not in data


def test_clone_embeds_note(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "base", {"X": "y"})
    clone_snapshot("base", "noted", snapshot_dir, note="my note")
    data = json.loads((snapshot_dir / "noted.json").read_text())
    assert data.get("_clone_note") == "my note"


def test_clone_without_note_has_no_note_key(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "base", {"X": "y"})
    clone_snapshot("base", "clean", snapshot_dir)
    data = json.loads((snapshot_dir / "clean.json").read_text())
    assert "_clone_note" not in data


def test_clone_returns_path_object(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "base", {})
    result = clone_snapshot("base", "dest", snapshot_dir)
    assert isinstance(result, Path)
