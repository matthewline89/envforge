"""Mirror (sync) snapshots between two snapshot directories."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from envforge.snapshot import load, save


class MirrorError(Exception):
    pass


@dataclass
class MirrorResult:
    source: str
    destination: str
    copied: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    overwritten: list[str] = field(default_factory=list)

    @property
    def total_copied(self) -> int:
        return len(self.copied)

    @property
    def total_skipped(self) -> int:
        return len(self.skipped)


def mirror_snapshots(
    source_dir: Path,
    dest_dir: Path,
    *,
    overwrite: bool = False,
    names: list[str] | None = None,
) -> MirrorResult:
    """Copy snapshots from source_dir to dest_dir.

    Args:
        source_dir: Directory containing source snapshot JSON files.
        dest_dir: Directory to copy snapshots into (created if missing).
        overwrite: If True, overwrite existing snapshots in dest_dir.
        names: Optional list of snapshot names to mirror; mirrors all if None.

    Returns:
        MirrorResult describing what was copied, skipped, or overwritten.
    """
    if not source_dir.is_dir():
        raise MirrorError(f"Source directory does not exist: {source_dir}")

    dest_dir.mkdir(parents=True, exist_ok=True)

    candidates = sorted(source_dir.glob("*.json"))
    if names is not None:
        name_set = set(names)
        candidates = [p for p in candidates if p.stem in name_set]

    result = MirrorResult(source=str(source_dir), destination=str(dest_dir))

    for src_path in candidates:
        dest_path = dest_dir / src_path.name
        if dest_path.exists() and not overwrite:
            result.skipped.append(src_path.stem)
            continue

        existed = dest_path.exists()
        shutil.copy2(src_path, dest_path)

        if existed:
            result.overwritten.append(src_path.stem)
        else:
            result.copied.append(src_path.stem)

    return result
