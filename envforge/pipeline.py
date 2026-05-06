"""Pipeline: chain multiple snapshots into an ordered processing pipeline."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class PipelineError(Exception):
    message: str

    def __str__(self) -> str:
        return self.message


@dataclass
class Pipeline:
    name: str
    steps: List[str] = field(default_factory=list)  # ordered snapshot names
    description: str = ""


def _pipelines_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "pipelines.json"


def _load_pipelines(snapshot_dir: Path) -> dict:
    p = _pipelines_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_pipelines(snapshot_dir: Path, data: dict) -> None:
    _pipelines_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def create_pipeline(snapshot_dir: Path, name: str, steps: List[str], description: str = "") -> Pipeline:
    data = _load_pipelines(snapshot_dir)
    if name in data:
        raise PipelineError(f"Pipeline '{name}' already exists")
    data[name] = {"steps": steps, "description": description}
    _save_pipelines(snapshot_dir, data)
    return Pipeline(name=name, steps=steps, description=description)


def get_pipeline(snapshot_dir: Path, name: str) -> Pipeline:
    data = _load_pipelines(snapshot_dir)
    if name not in data:
        raise PipelineError(f"Pipeline '{name}' not found")
    entry = data[name]
    return Pipeline(name=name, steps=entry["steps"], description=entry.get("description", ""))


def list_pipelines(snapshot_dir: Path) -> List[Pipeline]:
    data = _load_pipelines(snapshot_dir)
    return [Pipeline(name=k, steps=v["steps"], description=v.get("description", "")) for k, v in data.items()]


def delete_pipeline(snapshot_dir: Path, name: str) -> bool:
    data = _load_pipelines(snapshot_dir)
    if name not in data:
        return False
    del data[name]
    _save_pipelines(snapshot_dir, data)
    return True


def append_step(snapshot_dir: Path, name: str, snapshot_name: str) -> Pipeline:
    data = _load_pipelines(snapshot_dir)
    if name not in data:
        raise PipelineError(f"Pipeline '{name}' not found")
    data[name]["steps"].append(snapshot_name)
    _save_pipelines(snapshot_dir, data)
    entry = data[name]
    return Pipeline(name=name, steps=entry["steps"], description=entry.get("description", ""))
