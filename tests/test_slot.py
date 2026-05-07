"""Tests for envforge.slot."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.slot import (
    SlotError,
    list_slots,
    remove_slot,
    resolve_slot,
    set_slot,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_set_slot_creates_slots_file(snapshot_dir: Path) -> None:
    set_slot(snapshot_dir, "current", "snap_v1")
    assert (snapshot_dir / "_slots.json").exists()


def test_set_slot_stores_mapping(snapshot_dir: Path) -> None:
    set_slot(snapshot_dir, "current", "snap_v1")
    data = json.loads((snapshot_dir / "_slots.json").read_text())
    assert data["current"] == "snap_v1"


def test_set_slot_returns_true_when_new(snapshot_dir: Path) -> None:
    assert set_slot(snapshot_dir, "prod", "snap_prod") is True


def test_set_slot_returns_false_when_overwritten(snapshot_dir: Path) -> None:
    set_slot(snapshot_dir, "prod", "snap_prod")
    assert set_slot(snapshot_dir, "prod", "snap_prod_v2") is False


def test_set_slot_overwrites_existing(snapshot_dir: Path) -> None:
    set_slot(snapshot_dir, "staging", "snap_a")
    set_slot(snapshot_dir, "staging", "snap_b")
    assert resolve_slot(snapshot_dir, "staging") == "snap_b"


def test_remove_slot_returns_true_when_found(snapshot_dir: Path) -> None:
    set_slot(snapshot_dir, "dev", "snap_dev")
    assert remove_slot(snapshot_dir, "dev") is True


def test_remove_slot_returns_false_when_missing(snapshot_dir: Path) -> None:
    assert remove_slot(snapshot_dir, "nonexistent") is False


def test_remove_slot_deletes_entry(snapshot_dir: Path) -> None:
    set_slot(snapshot_dir, "dev", "snap_dev")
    remove_slot(snapshot_dir, "dev")
    assert resolve_slot(snapshot_dir, "dev") is None


def test_resolve_slot_returns_name(snapshot_dir: Path) -> None:
    set_slot(snapshot_dir, "latest", "snap_latest")
    assert resolve_slot(snapshot_dir, "latest") == "snap_latest"


def test_resolve_slot_returns_none_for_missing(snapshot_dir: Path) -> None:
    assert resolve_slot(snapshot_dir, "ghost") is None


def test_list_slots_returns_all_mappings(snapshot_dir: Path) -> None:
    set_slot(snapshot_dir, "a", "snap_a")
    set_slot(snapshot_dir, "b", "snap_b")
    result = list_slots(snapshot_dir)
    assert result == {"a": "snap_a", "b": "snap_b"}


def test_list_slots_returns_empty_when_no_file(snapshot_dir: Path) -> None:
    assert list_slots(snapshot_dir) == {}
