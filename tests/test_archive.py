"""Tests for envforge.archive."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from envforge.archive import ArchiveError, ArchiveResult, create_archive, extract_archive, list_archive


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _write(directory: Path, name: str, env: dict) -> Path:
    p = directory / f"{name}.json"
    p.write_text(json.dumps(env))
    return p


# --- create_archive ---

def test_create_archive_returns_archive_result(snapshot_dir, tmp_path):
    _write(snapshot_dir, "dev", {"A": "1"})
    result = create_archive(snapshot_dir, tmp_path / "out.zip")
    assert isinstance(result, ArchiveResult)


def test_create_archive_file_exists(snapshot_dir, tmp_path):
    _write(snapshot_dir, "dev", {"A": "1"})
    out = tmp_path / "out.zip"
    create_archive(snapshot_dir, out)
    assert out.exists()


def test_create_archive_includes_all_snapshots_by_default(snapshot_dir, tmp_path):
    _write(snapshot_dir, "dev", {"A": "1"})
    _write(snapshot_dir, "prod", {"B": "2"})
    result = create_archive(snapshot_dir, tmp_path / "out.zip")
    assert set(result.snapshots) == {"dev", "prod"}


def test_create_archive_filters_by_names(snapshot_dir, tmp_path):
    _write(snapshot_dir, "dev", {"A": "1"})
    _write(snapshot_dir, "prod", {"B": "2"})
    result = create_archive(snapshot_dir, tmp_path / "out.zip", names=["dev"])
    assert result.snapshots == ["dev"]


def test_create_archive_raises_for_missing_name(snapshot_dir, tmp_path):
    with pytest.raises(ArchiveError, match="not found"):
        create_archive(snapshot_dir, tmp_path / "out.zip", names=["ghost"])


def test_create_archive_raises_when_no_snapshots(snapshot_dir, tmp_path):
    with pytest.raises(ArchiveError, match="No snapshots"):
        create_archive(snapshot_dir, tmp_path / "out.zip")


# --- extract_archive ---

def test_extract_archive_restores_files(snapshot_dir, tmp_path):
    _write(snapshot_dir, "dev", {"X": "42"})
    archive = tmp_path / "bundle.zip"
    create_archive(snapshot_dir, archive)

    dest = tmp_path / "restored"
    result = extract_archive(archive, dest)
    assert (dest / "dev.json").exists()
    assert result.snapshots == ["dev"]


def test_extract_archive_preserves_env_data(snapshot_dir, tmp_path):
    _write(snapshot_dir, "dev", {"X": "42"})
    archive = tmp_path / "bundle.zip"
    create_archive(snapshot_dir, archive)

    dest = tmp_path / "restored"
    extract_archive(archive, dest)
    data = json.loads((dest / "dev.json").read_text())
    assert data["X"] == "42"


def test_extract_archive_raises_on_collision(snapshot_dir, tmp_path):
    _write(snapshot_dir, "dev", {"X": "1"})
    archive = tmp_path / "bundle.zip"
    create_archive(snapshot_dir, archive)
    extract_archive(archive, snapshot_dir)  # first extraction
    with pytest.raises(ArchiveError, match="already exists"):
        extract_archive(archive, snapshot_dir, overwrite=False)


def test_extract_archive_overwrite_replaces_file(snapshot_dir, tmp_path):
    _write(snapshot_dir, "dev", {"X": "1"})
    archive = tmp_path / "bundle.zip"
    create_archive(snapshot_dir, archive)
    extract_archive(archive, snapshot_dir, overwrite=True)  # should not raise


def test_extract_archive_raises_when_file_missing(tmp_path):
    with pytest.raises(ArchiveError, match="not found"):
        extract_archive(tmp_path / "ghost.zip", tmp_path / "dest")


# --- list_archive ---

def test_list_archive_returns_names(snapshot_dir, tmp_path):
    _write(snapshot_dir, "alpha", {})
    _write(snapshot_dir, "beta", {})
    archive = tmp_path / "bundle.zip"
    create_archive(snapshot_dir, archive)
    names = list_archive(archive)
    assert set(names) == {"alpha", "beta"}


def test_list_archive_raises_when_missing(tmp_path):
    with pytest.raises(ArchiveError, match="not found"):
        list_archive(tmp_path / "nope.zip")
