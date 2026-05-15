"""snapshot_copy.py — copy selected keys from one snapshot into another."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envforge.snapshot import load, save


class CopyError(Exception):
    def __str__(self) -> str:  # pragma: no cover
        return self.args[0]


@dataclass
class CopyResult:
    source: str
    destination: str
    keys_copied: List[str] = field(default_factory=list)
    keys_skipped: List[str] = field(default_factory=list)

    @property
    def total_copied(self) -> int:
        return len(self.keys_copied)

    @property
    def total_skipped(self) -> int:
        return len(self.keys_skipped)


def copy_keys(
    source: str,
    destination: str,
    keys: Optional[List[str]],
    overwrite: bool,
    snapshot_dir: str,
) -> CopyResult:
    """Copy *keys* from *source* snapshot into *destination* snapshot.

    Parameters
    ----------
    source:
        Name of the snapshot to read from.
    destination:
        Name of the snapshot to write into.  Created if it does not exist.
    keys:
        Explicit list of keys to copy.  ``None`` means copy all keys.
    overwrite:
        When *False*, keys that already exist in *destination* are skipped.
    snapshot_dir:
        Directory that contains snapshot JSON files.
    """
    src_env = load(source, snapshot_dir=snapshot_dir)
    if src_env is None:
        raise CopyError(f"Source snapshot '{source}' not found.")

    dst_env = load(destination, snapshot_dir=snapshot_dir) or {}

    candidates = keys if keys is not None else list(src_env.keys())

    result = CopyResult(source=source, destination=destination)

    for key in candidates:
        if key not in src_env:
            result.keys_skipped.append(key)
            continue
        if key in dst_env and not overwrite:
            result.keys_skipped.append(key)
            continue
        dst_env[key] = src_env[key]
        result.keys_copied.append(key)

    save(destination, dst_env, snapshot_dir=snapshot_dir)
    return result
