"""Preview a snapshot's contents with formatting options."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envforge.snapshot import load


@dataclass
class PreviewLine:
    key: str
    value: str
    masked: bool = False

    def display_value(self) -> str:
        if self.masked:
            return "*" * min(len(self.value), 8)
        return self.value


@dataclass
class SnapshotPreview:
    name: str
    lines: List[PreviewLine] = field(default_factory=list)
    truncated: bool = False

    def __len__(self) -> int:
        return len(self.lines)


_SENSITIVE_PATTERNS = ("secret", "password", "token", "key", "auth", "pass", "pwd")


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(pat in lower for pat in _SENSITIVE_PATTERNS)


def preview_snapshot(
    name: str,
    snapshot_dir: Path,
    *,
    mask_secrets: bool = True,
    limit: Optional[int] = None,
    key_filter: Optional[str] = None,
) -> SnapshotPreview:
    """Load and format a snapshot for display."""
    env: Dict[str, str] = load(name, snapshot_dir)

    lines: List[PreviewLine] = []
    for key, value in sorted(env.items()):
        if key_filter and key_filter.lower() not in key.lower():
            continue
        masked = mask_secrets and _is_sensitive(key)
        lines.append(PreviewLine(key=key, value=value, masked=masked))

    truncated = False
    if limit is not None and len(lines) > limit:
        lines = lines[:limit]
        truncated = True

    return SnapshotPreview(name=name, lines=lines, truncated=truncated)


def format_preview(preview: SnapshotPreview, *, show_index: bool = False) -> str:
    """Render a SnapshotPreview as a human-readable string."""
    rows = []
    for i, line in enumerate(preview.lines):
        prefix = f"{i + 1:>3}  " if show_index else ""
        rows.append(f"{prefix}{line.key}={line.display_value()}")
    if preview.truncated:
        rows.append("... (truncated)")
    return "\n".join(rows)
