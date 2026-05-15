"""Snapshot workflow: chain multiple operations into a named workflow."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class WorkflowError(Exception):
    def __str__(self) -> str:
        return self.args[0]


@dataclass
class WorkflowStep:
    operation: str  # e.g. "capture", "merge", "prune", "export"
    params: dict = field(default_factory=dict)


@dataclass
class Workflow:
    name: str
    description: str
    steps: List[WorkflowStep] = field(default_factory=list)


@dataclass
class WorkflowResult:
    workflow_name: str
    steps_run: int
    steps_skipped: int
    errors: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


def _workflows_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "workflows.json"


def _load_workflows(snapshot_dir: Path) -> dict:
    p = _workflows_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_workflows(snapshot_dir: Path, data: dict) -> None:
    _workflows_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def create_workflow(
    snapshot_dir: Path, name: str, description: str = ""
) -> bool:
    """Create a new empty workflow. Returns True if new, False if overwritten."""
    data = _load_workflows(snapshot_dir)
    is_new = name not in data
    data[name] = {"description": description, "steps": []}
    _save_workflows(snapshot_dir, data)
    return is_new


def append_step(
    snapshot_dir: Path, name: str, operation: str, params: Optional[dict] = None
) -> None:
    """Append a step to an existing workflow."""
    data = _load_workflows(snapshot_dir)
    if name not in data:
        raise WorkflowError(f"Workflow '{name}' not found")
    data[name]["steps"].append({"operation": operation, "params": params or {}})
    _save_workflows(snapshot_dir, data)


def get_workflow(snapshot_dir: Path, name: str) -> Workflow:
    """Load a workflow by name."""
    data = _load_workflows(snapshot_dir)
    if name not in data:
        raise WorkflowError(f"Workflow '{name}' not found")
    raw = data[name]
    steps = [WorkflowStep(**s) for s in raw.get("steps", [])]
    return Workflow(name=name, description=raw.get("description", ""), steps=steps)


def list_workflows(snapshot_dir: Path) -> List[str]:
    """Return all workflow names."""
    return list(_load_workflows(snapshot_dir).keys())


def delete_workflow(snapshot_dir: Path, name: str) -> bool:
    """Delete a workflow. Returns True if found and removed."""
    data = _load_workflows(snapshot_dir)
    if name not in data:
        return False
    del data[name]
    _save_workflows(snapshot_dir, data)
    return True
