"""Snapshot subscription: notify registered callbacks when snapshots change."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional


@dataclass
class SubscriptionEntry:
    name: str
    event: str  # "save", "delete", "any"
    label: Optional[str] = None


@dataclass
class SubscriptionReport:
    entries: List[SubscriptionEntry] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.entries) == 0

    def for_event(self, event: str) -> List[SubscriptionEntry]:
        return [e for e in self.entries if e.event in (event, "any")]


def _subscriptions_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "subscriptions.json"


def _load_subscriptions(snapshot_dir: Path) -> List[dict]:
    path = _subscriptions_path(snapshot_dir)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_subscriptions(snapshot_dir: Path, data: List[dict]) -> None:
    _subscriptions_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def subscribe(
    snapshot_dir: Path,
    name: str,
    event: str = "any",
    label: Optional[str] = None,
) -> bool:
    """Register a subscription. Returns True if new, False if updated."""
    data = _load_subscriptions(snapshot_dir)
    for entry in data:
        if entry["name"] == name and entry["event"] == event:
            entry["label"] = label
            _save_subscriptions(snapshot_dir, data)
            return False
    data.append({"name": name, "event": event, "label": label})
    _save_subscriptions(snapshot_dir, data)
    return True


def unsubscribe(snapshot_dir: Path, name: str, event: str = "any") -> bool:
    """Remove a subscription. Returns True if removed."""
    data = _load_subscriptions(snapshot_dir)
    before = len(data)
    data = [e for e in data if not (e["name"] == name and e["event"] == event)]
    if len(data) == before:
        return False
    _save_subscriptions(snapshot_dir, data)
    return True


def get_subscriptions(snapshot_dir: Path) -> SubscriptionReport:
    data = _load_subscriptions(snapshot_dir)
    entries = [SubscriptionEntry(**d) for d in data]
    return SubscriptionReport(entries=entries)


def notify(
    snapshot_dir: Path,
    event: str,
    callbacks: Dict[str, Callable[[SubscriptionEntry], None]],
) -> List[str]:
    """Fire callbacks for all subscriptions matching the event. Returns notified names."""
    report = get_subscriptions(snapshot_dir)
    notified: List[str] = []
    for entry in report.for_event(event):
        cb = callbacks.get(entry.name)
        if cb is not None:
            cb(entry)
            notified.append(entry.name)
    return notified
