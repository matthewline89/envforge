"""Tests for envforge.snapshot_chain."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_chain import (
    ChainError,
    Chain,
    ChainEntry,
    get_chain,
    link_snapshot,
    list_chains,
    unlink_snapshot,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_link_snapshot_creates_chains_file(snapshot_dir: Path) -> None:
    link_snapshot(snapshot_dir, "snap-a", None)
    assert (snapshot_dir / "chains.json").exists()


def test_link_snapshot_returns_true_when_new(snapshot_dir: Path) -> None:
    assert link_snapshot(snapshot_dir, "snap-a", None) is True


def test_link_snapshot_returns_false_when_updated(snapshot_dir: Path) -> None:
    link_snapshot(snapshot_dir, "snap-a", None)
    assert link_snapshot(snapshot_dir, "snap-a", "snap-b") is False


def test_link_snapshot_stores_parent(snapshot_dir: Path) -> None:
    link_snapshot(snapshot_dir, "snap-b", "snap-a")
    data = json.loads((snapshot_dir / "chains.json").read_text())
    assert data["snap-b"] == "snap-a"


def test_link_snapshot_root_has_none_parent(snapshot_dir: Path) -> None:
    link_snapshot(snapshot_dir, "snap-root", None)
    data = json.loads((snapshot_dir / "chains.json").read_text())
    assert data["snap-root"] is None


def test_unlink_snapshot_returns_true_when_found(snapshot_dir: Path) -> None:
    link_snapshot(snapshot_dir, "snap-a", None)
    assert unlink_snapshot(snapshot_dir, "snap-a") is True


def test_unlink_snapshot_returns_false_when_missing(snapshot_dir: Path) -> None:
    assert unlink_snapshot(snapshot_dir, "ghost") is False


def test_unlink_snapshot_removes_entry(snapshot_dir: Path) -> None:
    link_snapshot(snapshot_dir, "snap-a", None)
    unlink_snapshot(snapshot_dir, "snap-a")
    data = list_chains(snapshot_dir)
    assert "snap-a" not in data


def test_get_chain_raises_for_unknown(snapshot_dir: Path) -> None:
    with pytest.raises(ChainError, match="not part of any chain"):
        get_chain(snapshot_dir, "unknown")


def test_get_chain_single_root(snapshot_dir: Path) -> None:
    link_snapshot(snapshot_dir, "snap-a", None)
    chain = get_chain(snapshot_dir, "snap-a")
    assert isinstance(chain, Chain)
    assert chain.ordered_names() == ["snap-a"]


def test_get_chain_ordered_root_first(snapshot_dir: Path) -> None:
    link_snapshot(snapshot_dir, "snap-a", None)
    link_snapshot(snapshot_dir, "snap-b", "snap-a")
    link_snapshot(snapshot_dir, "snap-c", "snap-b")
    chain = get_chain(snapshot_dir, "snap-c")
    assert chain.ordered_names() == ["snap-a", "snap-b", "snap-c"]


def test_get_chain_detects_cycle(snapshot_dir: Path) -> None:
    # Manually inject a cycle
    chains_file = snapshot_dir / "chains.json"
    chains_file.write_text(json.dumps({"a": "b", "b": "a"}))
    with pytest.raises(ChainError, match="Cycle detected"):
        get_chain(snapshot_dir, "a")


def test_list_chains_returns_empty_when_no_file(snapshot_dir: Path) -> None:
    assert list_chains(snapshot_dir) == {}


def test_list_chains_returns_all_entries(snapshot_dir: Path) -> None:
    link_snapshot(snapshot_dir, "snap-a", None)
    link_snapshot(snapshot_dir, "snap-b", "snap-a")
    data = list_chains(snapshot_dir)
    assert "snap-a" in data
    assert "snap-b" in data
