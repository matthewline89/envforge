"""Named snapshot slots — assign a snapshot to a well-known slot name (e.g. 'current', 'staging')."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class SlotError(Exception):
    pass


def _slots_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "_slots.json"


def _load_slots(snapshot_dir: Path) -> dict[str, str]:
    p = _slots_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_slots(snapshot_dir: Path, slots: dict[str, str]) -> None:
    _slots_path(snapshot_dir).write_text(json.dumps(slots, indent=2))


def set_slot(snapshot_dir: Path, slot: str, snapshot_name: str) -> bool:
    """Assign *snapshot_name* to *slot*. Returns True if it is a new slot."""
    slots = _load_slots(snapshot_dir)
    is_new = slot not in slots
    slots[slot] = snapshot_name
    _save_slots(snapshot_dir, slots)
    return is_new


def remove_slot(snapshot_dir: Path, slot: str) -> bool:
    """Remove *slot*. Returns True if the slot existed."""
    slots = _load_slots(snapshot_dir)
    if slot not in slots:
        return False
    del slots[slot]
    _save_slots(snapshot_dir, slots)
    return True


def resolve_slot(snapshot_dir: Path, slot: str) -> Optional[str]:
    """Return the snapshot name assigned to *slot*, or None."""
    return _load_slots(snapshot_dir).get(slot)


def list_slots(snapshot_dir: Path) -> dict[str, str]:
    """Return all slot → snapshot mappings."""
    return _load_slots(snapshot_dir)
