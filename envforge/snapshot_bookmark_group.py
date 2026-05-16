"""snapshot_bookmark_group: cross-reference bookmarks with groups."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envforge.bookmark import _load_bookmarks
from envforge.group import _load_groups


@dataclass
class BookmarkGroupEntry:
    bookmark: str
    snapshot: str
    groups: List[str] = field(default_factory=list)


@dataclass
class BookmarkGroupReport:
    entries: List[BookmarkGroupEntry] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def for_bookmark(self, bookmark: str) -> BookmarkGroupEntry | None:
        for e in self.entries:
            if e.bookmark == bookmark:
                return e
        return None

    def bookmarks_in_group(self, group: str) -> List[str]:
        return [e.bookmark for e in self.entries if group in e.groups]


def build_report(snapshot_dir: Path) -> BookmarkGroupReport:
    """Build a report cross-referencing bookmarks with groups."""
    bookmarks = _load_bookmarks(snapshot_dir)
    groups_data = _load_groups(snapshot_dir)

    # invert groups: snapshot -> list of group names
    snapshot_to_groups: Dict[str, List[str]] = {}
    for group_name, members in groups_data.items():
        for snap in members:
            snapshot_to_groups.setdefault(snap, []).append(group_name)

    entries: List[BookmarkGroupEntry] = []
    for bm_name, snap_name in bookmarks.items():
        grps = snapshot_to_groups.get(snap_name, [])
        entries.append(BookmarkGroupEntry(
            bookmark=bm_name,
            snapshot=snap_name,
            groups=sorted(grps),
        ))

    return BookmarkGroupReport(entries=entries)
