"""Attach and retrieve free-form notes on snapshots."""
from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


class NoteError(Exception):
    pass


def _notes_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "notes.json"


def _load_notes(snapshot_dir: Path) -> dict[str, str]:
    p = _notes_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_notes(snapshot_dir: Path, notes: dict[str, str]) -> None:
    _notes_path(snapshot_dir).write_text(json.dumps(notes, indent=2))


def set_note(snapshot_dir: Path, name: str, text: str) -> bool:
    """Attach *text* as a note on *name*. Returns True if created, False if updated."""
    notes = _load_notes(snapshot_dir)
    is_new = name not in notes
    notes[name] = text
    _save_notes(snapshot_dir, notes)
    return is_new


def get_note(snapshot_dir: Path, name: str) -> Optional[str]:
    """Return the note for *name*, or None if absent."""
    return _load_notes(snapshot_dir).get(name)


def remove_note(snapshot_dir: Path, name: str) -> bool:
    """Remove the note for *name*. Returns True if it existed."""
    notes = _load_notes(snapshot_dir)
    if name not in notes:
        return False
    del notes[name]
    _save_notes(snapshot_dir, notes)
    return True


def list_notes(snapshot_dir: Path) -> dict[str, str]:
    """Return all snapshot-name → note mappings."""
    return dict(_load_notes(snapshot_dir))
