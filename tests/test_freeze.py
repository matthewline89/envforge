"""Tests for envforge.snapshot_freeze."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_freeze import (
    freeze_snapshot,
    unfreeze_snapshot,
    is_frozen,
    list_frozen,
    FreezeResult,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    snapshot_dir = tmp_path / ".envforge"
    snapshot_dir.mkdir()
    return snapshot_dir


def test_freeze_snapshot_creates_freeze_file(snapshot_dir: Path) -> None:
    freeze_snapshot(snapshot_dir, "dev")
    assert (snapshot_dir / "_freeze.json").exists()


def test_freeze_snapshot_stores_name(snapshot_dir: Path) -> None:
    freeze_snapshot(snapshot_dir, "dev")
    data = json.loads((snapshot_dir / "_freeze.json").read_text())
    assert "dev" in data


def test_freeze_snapshot_returns_true_when_new(snapshot_dir: Path) -> None:
    result = freeze_snapshot(snapshot_dir, "dev")
    assert isinstance(result, FreezeResult)
    assert result.frozen is True


def test_freeze_snapshot_returns_false_when_already_frozen(snapshot_dir: Path) -> None:
    freeze_snapshot(snapshot_dir, "dev")
    result = freeze_snapshot(snapshot_dir, "dev")
    assert result.frozen is False


def test_unfreeze_returns_true_when_found(snapshot_dir: Path) -> None:
    freeze_snapshot(snapshot_dir, "dev")
    assert unfreeze_snapshot(snapshot_dir, "dev") is True


def test_unfreeze_returns_false_when_not_frozen(snapshot_dir: Path) -> None:
    assert unfreeze_snapshot(snapshot_dir, "dev") is False


def test_unfreeze_removes_name(snapshot_dir: Path) -> None:
    freeze_snapshot(snapshot_dir, "dev")
    unfreeze_snapshot(snapshot_dir, "dev")
    assert "dev" not in list_frozen(snapshot_dir)


def test_is_frozen_true_after_freeze(snapshot_dir: Path) -> None:
    freeze_snapshot(snapshot_dir, "prod")
    assert is_frozen(snapshot_dir, "prod") is True


def test_is_frozen_false_before_freeze(snapshot_dir: Path) -> None:
    assert is_frozen(snapshot_dir, "prod") is False


def test_list_frozen_returns_empty_initially(snapshot_dir: Path) -> None:
    assert list_frozen(snapshot_dir) == []


def test_list_frozen_returns_all_names(snapshot_dir: Path) -> None:
    freeze_snapshot(snapshot_dir, "dev")
    freeze_snapshot(snapshot_dir, "prod")
    names = list_frozen(snapshot_dir)
    assert "dev" in names
    assert "prod" in names


def test_freeze_deduplicates_names(snapshot_dir: Path) -> None:
    freeze_snapshot(snapshot_dir, "dev")
    freeze_snapshot(snapshot_dir, "dev")
    names = list_frozen(snapshot_dir)
    assert names.count("dev") == 1
