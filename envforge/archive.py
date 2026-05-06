"""Archive and restore collections of snapshots as a single zip bundle."""

from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


class ArchiveError(Exception):
    """Raised when an archive operation fails."""


@dataclass
class ArchiveResult:
    path: Path
    snapshots: List[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.snapshots)


def create_archive(snapshot_dir: Path, archive_path: Path, names: List[str] | None = None) -> ArchiveResult:
    """Bundle one or more snapshots into a zip archive.

    Args:
        snapshot_dir: Directory that holds snapshot JSON files.
        archive_path: Destination path for the .zip file.
        names: Optional list of snapshot names to include. If None, all are included.

    Returns:
        ArchiveResult describing what was packed.
    """
    all_files = list(snapshot_dir.glob("*.json"))
    if names is not None:
        selected = [snapshot_dir / f"{n}.json" for n in names]
        missing = [p for p in selected if not p.exists()]
        if missing:
            raise ArchiveError(f"Snapshots not found: {[p.stem for p in missing]}")
        all_files = selected

    if not all_files:
        raise ArchiveError("No snapshots to archive.")

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    packed: List[str] = []
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for snap_file in all_files:
            zf.write(snap_file, arcname=snap_file.name)
            packed.append(snap_file.stem)

    return ArchiveResult(path=archive_path, snapshots=packed)


def extract_archive(archive_path: Path, snapshot_dir: Path, overwrite: bool = False) -> ArchiveResult:
    """Extract snapshots from a zip archive into snapshot_dir.

    Args:
        archive_path: Path to the .zip file.
        snapshot_dir: Directory where snapshots will be restored.
        overwrite: If False, raises ArchiveError on name collision.

    Returns:
        ArchiveResult describing what was unpacked.
    """
    if not archive_path.exists():
        raise ArchiveError(f"Archive not found: {archive_path}")

    snapshot_dir.mkdir(parents=True, exist_ok=True)
    restored: List[str] = []

    with zipfile.ZipFile(archive_path, "r") as zf:
        for member in zf.namelist():
            dest = snapshot_dir / member
            if dest.exists() and not overwrite:
                raise ArchiveError(
                    f"Snapshot '{dest.stem}' already exists. Use overwrite=True to replace it."
                )
            zf.extract(member, path=snapshot_dir)
            restored.append(dest.stem)

    return ArchiveResult(path=archive_path, snapshots=restored)


def list_archive(archive_path: Path) -> List[str]:
    """Return the snapshot names contained in an archive without extracting."""
    if not archive_path.exists():
        raise ArchiveError(f"Archive not found: {archive_path}")
    with zipfile.ZipFile(archive_path, "r") as zf:
        return [Path(n).stem for n in zf.namelist()]
