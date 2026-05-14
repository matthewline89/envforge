"""Build and query a dependency graph over snapshot chains."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from envforge.snapshot_chain import load_chains


@dataclass
class GraphNode:
    name: str
    parents: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)


@dataclass
class SnapshotGraph:
    nodes: Dict[str, GraphNode] = field(default_factory=dict)

    def roots(self) -> List[str]:
        """Return names of nodes with no parents."""
        return [n for n, node in self.nodes.items() if not node.parents]

    def leaves(self) -> List[str]:
        """Return names of nodes with no children."""
        return [n for n, node in self.nodes.items() if not node.children]

    def ancestors(self, name: str) -> List[str]:
        """Return all ancestor names in breadth-first order."""
        if name not in self.nodes:
            return []
        visited: List[str] = []
        queue = list(self.nodes[name].parents)
        seen: Set[str] = set()
        while queue:
            current = queue.pop(0)
            if current in seen:
                continue
            seen.add(current)
            visited.append(current)
            if current in self.nodes:
                queue.extend(self.nodes[current].parents)
        return visited

    def descendants(self, name: str) -> List[str]:
        """Return all descendant names in breadth-first order."""
        if name not in self.nodes:
            return []
        visited: List[str] = []
        queue = list(self.nodes[name].children)
        seen: Set[str] = set()
        while queue:
            current = queue.pop(0)
            if current in seen:
                continue
            seen.add(current)
            visited.append(current)
            if current in self.nodes:
                queue.extend(self.nodes[current].children)
        return visited


def build_graph(snapshot_dir: Path) -> SnapshotGraph:
    """Build a SnapshotGraph from all chains stored in *snapshot_dir*."""
    chains = load_chains(snapshot_dir)
    graph = SnapshotGraph()

    for name, entry in chains.items():
        if name not in graph.nodes:
            graph.nodes[name] = GraphNode(name=name)
        parent: Optional[str] = entry.parent
        if parent:
            if parent not in graph.nodes:
                graph.nodes[parent] = GraphNode(name=parent)
            graph.nodes[name].parents.append(parent)
            graph.nodes[parent].children.append(name)

    return graph
