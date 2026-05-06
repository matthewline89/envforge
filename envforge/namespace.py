"""Namespace support for grouping snapshots under logical project names."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_NAMESPACE_FILE = "namespaces.json"


def _ns_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _NAMESPACE_FILE


def _load_namespaces(snapshot_dir: Path) -> Dict[str, List[str]]:
    p = _ns_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_namespaces(snapshot_dir: Path, data: Dict[str, List[str]]) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    _ns_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def add_to_namespace(snapshot_dir: Path, namespace: str, snapshot_name: str) -> bool:
    """Add *snapshot_name* to *namespace*.  Returns True if it was newly added."""
    data = _load_namespaces(snapshot_dir)
    members = data.setdefault(namespace, [])
    if snapshot_name in members:
        return False
    members.append(snapshot_name)
    _save_namespaces(snapshot_dir, data)
    return True


def remove_from_namespace(snapshot_dir: Path, namespace: str, snapshot_name: str) -> bool:
    """Remove *snapshot_name* from *namespace*.  Returns True if it was present."""
    data = _load_namespaces(snapshot_dir)
    members = data.get(namespace, [])
    if snapshot_name not in members:
        return False
    members.remove(snapshot_name)
    if not members:
        del data[namespace]
    else:
        data[namespace] = members
    _save_namespaces(snapshot_dir, data)
    return True


def list_namespaces(snapshot_dir: Path) -> List[str]:
    """Return all namespace names."""
    return sorted(_load_namespaces(snapshot_dir).keys())


def members_of(snapshot_dir: Path, namespace: str) -> List[str]:
    """Return snapshot names belonging to *namespace*."""
    return list(_load_namespaces(snapshot_dir).get(namespace, []))


def namespace_of(snapshot_dir: Path, snapshot_name: str) -> Optional[str]:
    """Return the first namespace that contains *snapshot_name*, or None."""
    for ns, members in _load_namespaces(snapshot_dir).items():
        if snapshot_name in members:
            return ns
    return None
