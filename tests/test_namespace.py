"""Tests for envforge.namespace."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.namespace import (
    add_to_namespace,
    list_namespaces,
    members_of,
    namespace_of,
    remove_from_namespace,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def test_add_creates_namespaces_file(snapshot_dir: Path) -> None:
    add_to_namespace(snapshot_dir, "backend", "prod")
    assert (snapshot_dir / "namespaces.json").exists()


def test_add_stores_snapshot_in_namespace(snapshot_dir: Path) -> None:
    add_to_namespace(snapshot_dir, "backend", "prod")
    data = json.loads((snapshot_dir / "namespaces.json").read_text())
    assert "prod" in data["backend"]


def test_add_returns_true_when_new(snapshot_dir: Path) -> None:
    assert add_to_namespace(snapshot_dir, "backend", "prod") is True


def test_add_returns_false_when_duplicate(snapshot_dir: Path) -> None:
    add_to_namespace(snapshot_dir, "backend", "prod")
    assert add_to_namespace(snapshot_dir, "backend", "prod") is False


def test_add_multiple_snapshots_to_same_namespace(snapshot_dir: Path) -> None:
    add_to_namespace(snapshot_dir, "backend", "prod")
    add_to_namespace(snapshot_dir, "backend", "staging")
    assert members_of(snapshot_dir, "backend") == ["prod", "staging"]


def test_remove_returns_true_when_found(snapshot_dir: Path) -> None:
    add_to_namespace(snapshot_dir, "backend", "prod")
    assert remove_from_namespace(snapshot_dir, "backend", "prod") is True


def test_remove_returns_false_when_not_found(snapshot_dir: Path) -> None:
    assert remove_from_namespace(snapshot_dir, "backend", "missing") is False


def test_remove_deletes_empty_namespace(snapshot_dir: Path) -> None:
    add_to_namespace(snapshot_dir, "backend", "prod")
    remove_from_namespace(snapshot_dir, "backend", "prod")
    assert "backend" not in list_namespaces(snapshot_dir)


def test_list_namespaces_returns_sorted(snapshot_dir: Path) -> None:
    add_to_namespace(snapshot_dir, "zebra", "s1")
    add_to_namespace(snapshot_dir, "alpha", "s2")
    assert list_namespaces(snapshot_dir) == ["alpha", "zebra"]


def test_list_namespaces_empty_dir(snapshot_dir: Path) -> None:
    assert list_namespaces(snapshot_dir) == []


def test_members_of_unknown_namespace(snapshot_dir: Path) -> None:
    assert members_of(snapshot_dir, "ghost") == []


def test_namespace_of_returns_correct_ns(snapshot_dir: Path) -> None:
    add_to_namespace(snapshot_dir, "frontend", "dev")
    assert namespace_of(snapshot_dir, "dev") == "frontend"


def test_namespace_of_returns_none_when_missing(snapshot_dir: Path) -> None:
    assert namespace_of(snapshot_dir, "unknown") is None
