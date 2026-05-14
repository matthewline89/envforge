"""Tests for envforge.snapshot_graph."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from envforge.snapshot_chain import ChainEntry
from envforge.snapshot_graph import SnapshotGraph, GraphNode, build_graph


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _fake_chains(mapping: dict):
    """Patch load_chains to return *mapping*."""
    return patch("envforge.snapshot_graph.load_chains", return_value=mapping)


def test_build_graph_returns_snapshot_graph(snapshot_dir):
    with _fake_chains({}):
        result = build_graph(snapshot_dir)
    assert isinstance(result, SnapshotGraph)


def test_build_graph_empty_chains_has_no_nodes(snapshot_dir):
    with _fake_chains({}):
        graph = build_graph(snapshot_dir)
    assert graph.nodes == {}


def test_build_graph_creates_node_for_each_name(snapshot_dir):
    chains = {
        "snap_a": ChainEntry(name="snap_a", parent=None),
        "snap_b": ChainEntry(name="snap_b", parent=None),
    }
    with _fake_chains(chains):
        graph = build_graph(snapshot_dir)
    assert "snap_a" in graph.nodes
    assert "snap_b" in graph.nodes


def test_build_graph_links_parent_and_child(snapshot_dir):
    chains = {
        "child": ChainEntry(name="child", parent="parent"),
        "parent": ChainEntry(name="parent", parent=None),
    }
    with _fake_chains(chains):
        graph = build_graph(snapshot_dir)
    assert "parent" in graph.nodes["child"].parents
    assert "child" in graph.nodes["parent"].children


def test_roots_returns_nodes_without_parents(snapshot_dir):
    chains = {
        "root": ChainEntry(name="root", parent=None),
        "leaf": ChainEntry(name="leaf", parent="root"),
    }
    with _fake_chains(chains):
        graph = build_graph(snapshot_dir)
    assert graph.roots() == ["root"]


def test_leaves_returns_nodes_without_children(snapshot_dir):
    chains = {
        "root": ChainEntry(name="root", parent=None),
        "leaf": ChainEntry(name="leaf", parent="root"),
    }
    with _fake_chains(chains):
        graph = build_graph(snapshot_dir)
    assert graph.leaves() == ["leaf"]


def test_ancestors_returns_empty_for_root(snapshot_dir):
    graph = SnapshotGraph(nodes={"root": GraphNode(name="root")})
    assert graph.ancestors("root") == []


def test_ancestors_returns_parent_chain():
    graph = SnapshotGraph(nodes={
        "a": GraphNode(name="a"),
        "b": GraphNode(name="b", parents=["a"]),
        "c": GraphNode(name="c", parents=["b"]),
    })
    result = graph.ancestors("c")
    assert "b" in result
    assert "a" in result


def test_descendants_returns_child_chain():
    graph = SnapshotGraph(nodes={
        "a": GraphNode(name="a", children=["b"]),
        "b": GraphNode(name="b", children=["c"]),
        "c": GraphNode(name="c"),
    })
    result = graph.descendants("a")
    assert "b" in result
    assert "c" in result


def test_ancestors_unknown_node_returns_empty():
    graph = SnapshotGraph()
    assert graph.ancestors("nonexistent") == []


def test_descendants_unknown_node_returns_empty():
    graph = SnapshotGraph()
    assert graph.descendants("nonexistent") == []
