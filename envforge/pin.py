"""Pin a snapshot to a named version slot (e.g. 'stable', 'prod')."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

_PINS_FILE = "pins.json"


def _pins_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _PINS_FILE


def _load_pins(snapshot_dir: Path) -> dict[str, str]:
    path = _pins_path(snapshot_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_pins(snapshot_dir: Path, pins: dict[str, str]) -> None:
    _pins_path(snapshot_dir).write_text(json.dumps(pins, indent=2))


def set_pin(snapshot_dir: Path, pin_name: str, snapshot_name: str) -> None:
    """Associate *pin_name* with *snapshot_name*."""
    pins = _load_pins(snapshot_dir)
    pins[pin_name] = snapshot_name
    _save_pins(snapshot_dir, pins)


def remove_pin(snapshot_dir: Path, pin_name: str) -> bool:
    """Remove *pin_name*. Returns True if it existed."""
    pins = _load_pins(snapshot_dir)
    if pin_name not in pins:
        return False
    del pins[pin_name]
    _save_pins(snapshot_dir, pins)
    return True


def resolve_pin(snapshot_dir: Path, pin_name: str) -> Optional[str]:
    """Return the snapshot name for *pin_name*, or None."""
    return _load_pins(snapshot_dir).get(pin_name)


def list_pins(snapshot_dir: Path) -> dict[str, str]:
    """Return all pin → snapshot mappings."""
    return _load_pins(snapshot_dir)
