"""Tests for the snapshot module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot import capture, delete, list_snapshots, load, save


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def test_capture_uses_provided_env():
    env = {"FOO": "bar", "BAZ": "qux"}
    snap = capture("test-snap", env=env)
    assert snap["name"] == "test-snap"
    assert snap["variables"] == env
    assert "created_at" in snap


def test_capture_falls_back_to_os_environ():
    import os
    snap = capture("live")
    assert snap["variables"] == dict(os.environ)


def test_save_creates_file(snapshot_dir: Path):
    snap = capture("my-project", env={"KEY": "value"})
    path = save(snap, snapshot_dir=snapshot_dir)
    assert path.exists()
    assert path.name == "my-project.json"


def test_save_writes_valid_json(snapshot_dir: Path):
    snap = capture("proj", env={"A": "1"})
    path = save(snap, snapshot_dir=snapshot_dir)
    data = json.loads(path.read_text())
    assert data["variables"] == {"A": "1"}


def test_load_returns_snapshot(snapshot_dir: Path):
    snap = capture("load-test", env={"X": "42"})
    save(snap, snapshot_dir=snapshot_dir)
    loaded = load("load-test", snapshot_dir=snapshot_dir)
    assert loaded["variables"]["X"] == "42"


def test_load_raises_for_missing_snapshot(snapshot_dir: Path):
    with pytest.raises(FileNotFoundError, match="missing-snap"):
        load("missing-snap", snapshot_dir=snapshot_dir)


def test_list_snapshots_returns_metadata(snapshot_dir: Path):
    save(capture("alpha", env={"A": "1", "B": "2"}), snapshot_dir=snapshot_dir)
    save(capture("beta", env={"C": "3"}), snapshot_dir=snapshot_dir)
    results = list_snapshots(snapshot_dir=snapshot_dir)
    names = [r["name"] for r in results]
    assert "alpha" in names
    assert "beta" in names
    assert results[0]["var_count"] >= 1


def test_list_snapshots_empty_dir(snapshot_dir: Path):
    assert list_snapshots(snapshot_dir=snapshot_dir) == []


def test_delete_removes_file(snapshot_dir: Path):
    save(capture("to-delete", env={}), snapshot_dir=snapshot_dir)
    delete("to-delete", snapshot_dir=snapshot_dir)
    with pytest.raises(FileNotFoundError):
        load("to-delete", snapshot_dir=snapshot_dir)


def test_delete_raises_for_missing(snapshot_dir: Path):
    with pytest.raises(FileNotFoundError):
        delete("ghost", snapshot_dir=snapshot_dir)


def test_name_with_spaces_is_sanitised(snapshot_dir: Path):
    snap = capture("my project", env={"ENV": "prod"})
    path = save(snap, snapshot_dir=snapshot_dir)
    assert path.name == "my_project.json"
    loaded = load("my project", snapshot_dir=snapshot_dir)
    assert loaded["name"] == "my project"
