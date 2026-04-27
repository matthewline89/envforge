"""Compare multiple snapshots side-by-side and produce a unified report."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from envforge.snapshot import load


@dataclass
class CompareReport:
    """Unified comparison report for two or more snapshots."""

    snapshot_names: List[str]
    # key -> {snapshot_name -> value or None}
    matrix: Dict[str, Dict[str, Optional[str]]] = field(default_factory=dict)

    def all_keys(self) -> Set[str]:
        return set(self.matrix.keys())

    def common_keys(self) -> Set[str]:
        """Keys present in every snapshot."""
        if not self.snapshot_names:
            return set()
        return {
            k
            for k, vals in self.matrix.items()
            if all(vals.get(n) is not None for n in self.snapshot_names)
        }

    def unique_keys(self) -> Dict[str, Set[str]]:
        """Keys that appear in exactly one snapshot."""
        result: Dict[str, Set[str]] = {n: set() for n in self.snapshot_names}
        for key, vals in self.matrix.items():
            present = [n for n in self.snapshot_names if vals.get(n) is not None]
            if len(present) == 1:
                result[present[0]].add(key)
        return result

    def differing_keys(self) -> Set[str]:
        """Keys present in all snapshots but with at least one differing value."""
        result = set()
        for key in self.common_keys():
            vals = [self.matrix[key].get(n) for n in self.snapshot_names]
            if len(set(v for v in vals if v is not None)) > 1:
                result.add(key)
        return result


def build_matrix(
    snapshot_names: List[str], snapshot_dir: object
) -> Dict[str, Dict[str, Optional[str]]]:
    """Load each snapshot and build a key -> {name -> value} matrix."""
    all_data: Dict[str, Dict[str, str]] = {}
    for name in snapshot_names:
        all_data[name] = load(name, snapshot_dir=snapshot_dir)

    all_keys: Set[str] = set()
    for data in all_data.values():
        all_keys.update(data.keys())

    matrix: Dict[str, Dict[str, Optional[str]]] = {}
    for key in sorted(all_keys):
        matrix[key] = {name: all_data[name].get(key) for name in snapshot_names}
    return matrix


def compare_snapshots(
    snapshot_names: List[str], snapshot_dir: object
) -> CompareReport:
    """Compare two or more snapshots and return a CompareReport."""
    if len(snapshot_names) < 2:
        raise ValueError("At least two snapshot names are required for comparison.")
    matrix = build_matrix(snapshot_names, snapshot_dir)
    return CompareReport(snapshot_names=list(snapshot_names), matrix=matrix)
