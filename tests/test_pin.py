"""Unit tests for envforge.pin."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.pin import (
    set_pin,
    remove_pin,
    resolve_pin,
    list_pins,
    _pins_path,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    snapshot_dir = tmp_path / ".envforge"
    snapshot_dir.mkdir()
    return snapshot_dir


def test_set_pin_creates_pins_file(snapshot_dir: Path) -> None:
    set_pin(snapshot_dir, "stable", "snap_001")
    assert _pins_path(snapshot_dir).exists()


def test_set_pin_stores_mapping(snapshot_dir: Path) -> None:
    set_pin(snapshot_dir, "stable", "snap_001")
    data = json.loads(_pins_path(snapshot_dir).read_text())
    assert data["stable"] == "snap_001"


def test_set_pin_overwrites_existing(snapshot_dir: Path) -> None:
    set_pin(snapshot_dir, "stable", "snap_001")
    set_pin(snapshot_dir, "stable", "snap_002")
    assert resolve_pin(snapshot_dir, "stable") == "snap_002"


def test_remove_pin_returns_true_when_found(snapshot_dir: Path) -> None:
    set_pin(snapshot_dir, "prod", "snap_010")
    assert remove_pin(snapshot_dir, "prod") is True


def test_remove_pin_returns_false_when_missing(snapshot_dir: Path) -> None:
    assert remove_pin(snapshot_dir, "nonexistent") is False


def test_remove_pin_deletes_entry(snapshot_dir: Path) -> None:
    set_pin(snapshot_dir, "prod", "snap_010")
    remove_pin(snapshot_dir, "prod")
    assert resolve_pin(snapshot_dir, "prod") is None


def test_resolve_pin_returns_none_for_missing(snapshot_dir: Path) -> None:
    assert resolve_pin(snapshot_dir, "missing") is None


def test_list_pins_returns_empty_when_no_file(snapshot_dir: Path) -> None:
    assert list_pins(snapshot_dir) == {}


def test_list_pins_returns_all_entries(snapshot_dir: Path) -> None:
    set_pin(snapshot_dir, "stable", "snap_001")
    set_pin(snapshot_dir, "prod", "snap_002")
    pins = list_pins(snapshot_dir)
    assert pins == {"stable": "snap_001", "prod": "snap_002"}


def test_multiple_pins_coexist(snapshot_dir: Path) -> None:
    set_pin(snapshot_dir, "a", "snap_a")
    set_pin(snapshot_dir, "b", "snap_b")
    assert resolve_pin(snapshot_dir, "a") == "snap_a"
    assert resolve_pin(snapshot_dir, "b") == "snap_b"
