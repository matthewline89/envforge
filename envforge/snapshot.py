"""Snapshot module for capturing and storing environment variable sets."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_SNAPSHOT_DIR = Path.home() / ".envforge" / "snapshots"


def capture(name: str, env: Optional[dict[str, str]] = None) -> dict:
    """Capture current (or provided) environment variables into a snapshot dict."""
    env_vars = env if env is not None else dict(os.environ)
    return {
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "variables": env_vars,
    }


def save(snapshot: dict, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> Path:
    """Persist a snapshot to disk as a JSON file."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    safe_name = snapshot["name"].replace(" ", "_").replace("/", "-")
    file_path = snapshot_dir / f"{safe_name}.json"
    file_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return file_path


def load(name: str, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> dict:
    """Load a snapshot from disk by name."""
    safe_name = name.replace(" ", "_").replace("/", "-")
    file_path = snapshot_dir / f"{safe_name}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found at {file_path}")
    return json.loads(file_path.read_text(encoding="utf-8"))


def list_snapshots(snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> list[dict]:
    """Return metadata for all saved snapshots, sorted by creation time."""
    if not snapshot_dir.exists():
        return []
    snapshots = []
    for file_path in snapshot_dir.glob("*.json"):
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            snapshots.append({
                "name": data.get("name", file_path.stem),
                "created_at": data.get("created_at", ""),
                "var_count": len(data.get("variables", {})),
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return sorted(snapshots, key=lambda s: s["created_at"])


def delete(name: str, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> None:
    """Delete a snapshot file by name."""
    safe_name = name.replace(" ", "_").replace("/", "-")
    file_path = snapshot_dir / f"{safe_name}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found at {file_path}")
    file_path.unlink()
