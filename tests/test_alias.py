"""Tests for envforge.alias module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.alias import (
    list_aliases,
    remove_alias,
    resolve_alias,
    resolve_name_or_alias,
    set_alias,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def test_set_alias_creates_aliases_file(snapshot_dir: Path) -> None:
    set_alias(snapshot_dir, "prod", "production-2024-01")
    assert (snapshot_dir / "aliases.json").exists()


def test_set_alias_stores_mapping(snapshot_dir: Path) -> None:
    set_alias(snapshot_dir, "dev", "development-local")
    data = json.loads((snapshot_dir / "aliases.json").read_text())
    assert data["dev"] == "development-local"


def test_set_alias_overwrites_existing(snapshot_dir: Path) -> None:
    set_alias(snapshot_dir, "prod", "snap-v1")
    set_alias(snapshot_dir, "prod", "snap-v2")
    assert resolve_alias(snapshot_dir, "prod") == "snap-v2"


def test_remove_alias_returns_true_when_found(snapshot_dir: Path) -> None:
    set_alias(snapshot_dir, "staging", "staging-2024")
    assert remove_alias(snapshot_dir, "staging") is True


def test_remove_alias_returns_false_when_missing(snapshot_dir: Path) -> None:
    assert remove_alias(snapshot_dir, "nonexistent") is False


def test_remove_alias_deletes_entry(snapshot_dir: Path) -> None:
    set_alias(snapshot_dir, "qa", "qa-snapshot")
    remove_alias(snapshot_dir, "qa")
    assert resolve_alias(snapshot_dir, "qa") is None


def test_resolve_alias_returns_none_for_missing(snapshot_dir: Path) -> None:
    assert resolve_alias(snapshot_dir, "missing") is None


def test_list_aliases_empty_dir(snapshot_dir: Path) -> None:
    assert list_aliases(snapshot_dir) == {}


def test_list_aliases_returns_all(snapshot_dir: Path) -> None:
    set_alias(snapshot_dir, "a", "snap-a")
    set_alias(snapshot_dir, "b", "snap-b")
    result = list_aliases(snapshot_dir)
    assert result == {"a": "snap-a", "b": "snap-b"}


def test_resolve_name_or_alias_returns_alias_target(snapshot_dir: Path) -> None:
    set_alias(snapshot_dir, "live", "production-snapshot")
    assert resolve_name_or_alias(snapshot_dir, "live") == "production-snapshot"


def test_resolve_name_or_alias_passthrough_when_not_alias(snapshot_dir: Path) -> None:
    assert resolve_name_or_alias(snapshot_dir, "direct-name") == "direct-name"
