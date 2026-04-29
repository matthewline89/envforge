"""Tests for envforge.audit."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.audit import (
    AuditEntry,
    _audit_path,
    clear_audit_log,
    get_audit_log,
    record_action,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def test_record_action_creates_audit_file(snapshot_dir: Path) -> None:
    record_action(snapshot_dir, "save", "my_snap")
    assert _audit_path(snapshot_dir).exists()


def test_record_action_returns_entry(snapshot_dir: Path) -> None:
    entry = record_action(snapshot_dir, "save", "my_snap")
    assert isinstance(entry, AuditEntry)
    assert entry.action == "save"
    assert entry.snapshot == "my_snap"


def test_record_action_stores_user(snapshot_dir: Path) -> None:
    entry = record_action(snapshot_dir, "load", "snap", user="alice")
    assert entry.user == "alice"


def test_record_action_stores_note(snapshot_dir: Path) -> None:
    entry = record_action(snapshot_dir, "delete", "snap", note="cleanup")
    assert entry.note == "cleanup"


def test_record_action_appends_multiple(snapshot_dir: Path) -> None:
    record_action(snapshot_dir, "save", "a")
    record_action(snapshot_dir, "load", "b")
    raw = json.loads(_audit_path(snapshot_dir).read_text())
    assert len(raw) == 2


def test_record_action_has_timestamp(snapshot_dir: Path) -> None:
    entry = record_action(snapshot_dir, "save", "snap")
    assert "T" in entry.timestamp  # ISO format


def test_get_audit_log_returns_all(snapshot_dir: Path) -> None:
    record_action(snapshot_dir, "save", "a")
    record_action(snapshot_dir, "load", "b")
    entries = get_audit_log(snapshot_dir)
    assert len(entries) == 2


def test_get_audit_log_filters_by_snapshot(snapshot_dir: Path) -> None:
    record_action(snapshot_dir, "save", "alpha")
    record_action(snapshot_dir, "save", "beta")
    entries = get_audit_log(snapshot_dir, snapshot="alpha")
    assert len(entries) == 1
    assert entries[0].snapshot == "alpha"


def test_get_audit_log_filters_by_action(snapshot_dir: Path) -> None:
    record_action(snapshot_dir, "save", "snap")
    record_action(snapshot_dir, "delete", "snap")
    entries = get_audit_log(snapshot_dir, action="delete")
    assert len(entries) == 1
    assert entries[0].action == "delete"


def test_get_audit_log_empty_when_no_file(snapshot_dir: Path) -> None:
    entries = get_audit_log(snapshot_dir)
    assert entries == []


def test_clear_audit_log_returns_count(snapshot_dir: Path) -> None:
    record_action(snapshot_dir, "save", "a")
    record_action(snapshot_dir, "save", "b")
    count = clear_audit_log(snapshot_dir)
    assert count == 2


def test_clear_audit_log_empties_file(snapshot_dir: Path) -> None:
    record_action(snapshot_dir, "save", "snap")
    clear_audit_log(snapshot_dir)
    assert get_audit_log(snapshot_dir) == []
