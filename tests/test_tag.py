"""Tests for envforge.tag module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.tag import (
    add_tag,
    list_tags,
    remove_tag,
    resolve_tag,
    tags_for_snapshot,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def test_add_tag_creates_tags_file(snapshot_dir: Path) -> None:
    add_tag(snapshot_dir, "prod", "snap_prod")
    tags_file = snapshot_dir / "tags.json"
    assert tags_file.exists()


def test_add_tag_stores_mapping(snapshot_dir: Path) -> None:
    add_tag(snapshot_dir, "prod", "snap_prod")
    tags = list_tags(snapshot_dir)
    assert tags["prod"] == "snap_prod"


def test_add_tag_overwrites_existing(snapshot_dir: Path) -> None:
    add_tag(snapshot_dir, "prod", "snap_v1")
    add_tag(snapshot_dir, "prod", "snap_v2")
    assert resolve_tag(snapshot_dir, "prod") == "snap_v2"


def test_remove_tag_returns_true_when_found(snapshot_dir: Path) -> None:
    add_tag(snapshot_dir, "staging", "snap_staging")
    result = remove_tag(snapshot_dir, "staging")
    assert result is True


def test_remove_tag_deletes_mapping(snapshot_dir: Path) -> None:
    add_tag(snapshot_dir, "staging", "snap_staging")
    remove_tag(snapshot_dir, "staging")
    assert resolve_tag(snapshot_dir, "staging") is None


def test_remove_tag_returns_false_when_missing(snapshot_dir: Path) -> None:
    result = remove_tag(snapshot_dir, "nonexistent")
    assert result is False


def test_resolve_tag_returns_none_for_unknown(snapshot_dir: Path) -> None:
    assert resolve_tag(snapshot_dir, "ghost") is None


def test_list_tags_empty_when_no_file(snapshot_dir: Path) -> None:
    assert list_tags(snapshot_dir) == {}


def test_list_tags_returns_all_entries(snapshot_dir: Path) -> None:
    add_tag(snapshot_dir, "a", "snap_a")
    add_tag(snapshot_dir, "b", "snap_b")
    tags = list_tags(snapshot_dir)
    assert len(tags) == 2
    assert tags["a"] == "snap_a"
    assert tags["b"] == "snap_b"


def test_tags_for_snapshot_returns_matching_tags(snapshot_dir: Path) -> None:
    add_tag(snapshot_dir, "latest", "snap_x")
    add_tag(snapshot_dir, "stable", "snap_x")
    add_tag(snapshot_dir, "other", "snap_y")
    result = tags_for_snapshot(snapshot_dir, "snap_x")
    assert sorted(result) == ["latest", "stable"]


def test_tags_for_snapshot_empty_when_none_match(snapshot_dir: Path) -> None:
    add_tag(snapshot_dir, "prod", "snap_prod")
    assert tags_for_snapshot(snapshot_dir, "snap_missing") == []
