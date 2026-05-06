"""Tests for envforge.expire."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envforge.expire import (
    ExpireResult,
    get_expiry,
    is_expired,
    list_expiry,
    purge_expired,
    set_expiry,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


def _future(seconds: int = 3600) -> datetime:
    return datetime.now(timezone.utc) + timedelta(seconds=seconds)


def _past(seconds: int = 3600) -> datetime:
    return datetime.now(timezone.utc) - timedelta(seconds=seconds)


def test_set_expiry_creates_expiry_file(snapshot_dir: Path) -> None:
    set_expiry(snapshot_dir, "snap1", _future())
    assert (snapshot_dir / "expiry.json").exists()


def test_set_expiry_stores_timestamp(snapshot_dir: Path) -> None:
    exp = _future()
    set_expiry(snapshot_dir, "snap1", exp)
    stored = get_expiry(snapshot_dir, "snap1")
    assert stored is not None
    assert abs((stored - exp).total_seconds()) < 1


def test_get_expiry_returns_none_for_unknown(snapshot_dir: Path) -> None:
    assert get_expiry(snapshot_dir, "missing") is None


def test_is_expired_false_for_future(snapshot_dir: Path) -> None:
    set_expiry(snapshot_dir, "snap1", _future())
    assert is_expired(snapshot_dir, "snap1") is False


def test_is_expired_true_for_past(snapshot_dir: Path) -> None:
    set_expiry(snapshot_dir, "snap1", _past())
    assert is_expired(snapshot_dir, "snap1") is True


def test_is_expired_false_when_no_expiry_set(snapshot_dir: Path) -> None:
    assert is_expired(snapshot_dir, "snap_no_ttl") is False


def test_list_expiry_returns_all_entries(snapshot_dir: Path) -> None:
    set_expiry(snapshot_dir, "a", _future(100))
    set_expiry(snapshot_dir, "b", _future(200))
    mapping = list_expiry(snapshot_dir)
    assert set(mapping.keys()) == {"a", "b"}
    assert all(isinstance(v, datetime) for v in mapping.values())


def test_purge_expired_removes_snapshot_file(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "old", {"KEY": "val"})
    set_expiry(snapshot_dir, "old", _past())
    result = purge_expired(snapshot_dir)
    assert "old" in result.removed
    assert not (snapshot_dir / "old.json").exists()


def test_purge_expired_keeps_future_snapshot(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "new", {"KEY": "val"})
    set_expiry(snapshot_dir, "new", _future())
    result = purge_expired(snapshot_dir)
    assert "new" not in result.removed
    assert (snapshot_dir / "new.json").exists()


def test_purge_expired_removes_entry_from_expiry_file(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "old", {})
    set_expiry(snapshot_dir, "old", _past())
    purge_expired(snapshot_dir)
    assert get_expiry(snapshot_dir, "old") is None


def test_expire_result_total_removed(snapshot_dir: Path) -> None:
    for name in ("x", "y", "z"):
        _write(snapshot_dir, name, {})
        set_expiry(snapshot_dir, name, _past())
    result = purge_expired(snapshot_dir)
    assert result.total_removed == 3


def test_purge_handles_missing_snapshot_file_gracefully(snapshot_dir: Path) -> None:
    # Expiry entry exists but the .json file was already deleted
    set_expiry(snapshot_dir, "ghost", _past())
    result = purge_expired(snapshot_dir)
    assert "ghost" in result.removed
