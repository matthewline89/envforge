"""Tests for envforge.snapshot_health."""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

import pytest

from envforge.snapshot_health import check_health, HealthReport


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


def _write_expiry(snapshot_dir: Path, name: str, iso: str) -> None:
    path = snapshot_dir / "expiry.json"
    data = json.loads(path.read_text()) if path.exists() else {}
    data[name] = iso
    path.write_text(json.dumps(data))


def _past_iso() -> str:
    return (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()


def test_check_health_returns_health_report(snapshot_dir):
    _write(snapshot_dir, "mysnap", {"KEY": "val"})
    report = check_health("mysnap", snapshot_dir)
    assert isinstance(report, HealthReport)


def test_check_health_name_matches(snapshot_dir):
    _write(snapshot_dir, "mysnap", {"KEY": "val"})
    report = check_health("mysnap", snapshot_dir)
    assert report.name == "mysnap"


def test_check_health_ok_for_clean_snapshot(snapshot_dir):
    _write(snapshot_dir, "clean", {"KEY": "value"})
    report = check_health("clean", snapshot_dir)
    assert report.status == "ok"
    assert report.healthy is True


def test_check_health_expired_snapshot(snapshot_dir):
    _write(snapshot_dir, "old", {"KEY": "value"})
    _write_expiry(snapshot_dir, "old", _past_iso())
    report = check_health("old", snapshot_dir)
    assert report.expired is True
    assert report.status == "expired"
    assert report.healthy is False


def test_check_health_not_expired_by_default(snapshot_dir):
    _write(snapshot_dir, "fresh", {"KEY": "value"})
    report = check_health("fresh", snapshot_dir)
    assert report.expired is False


def test_check_health_locked_false_by_default(snapshot_dir):
    _write(snapshot_dir, "snap", {"A": "1"})
    report = check_health("snap", snapshot_dir)
    assert report.locked is False


def test_check_health_frozen_false_by_default(snapshot_dir):
    _write(snapshot_dir, "snap", {"A": "1"})
    report = check_health("snap", snapshot_dir)
    assert report.frozen is False


def test_check_health_empty_value_produces_warning(snapshot_dir):
    _write(snapshot_dir, "snap", {"EMPTY": ""})
    report = check_health("snap", snapshot_dir)
    assert report.status == "warning"
    assert any("empty" in w.lower() for w in report.warnings)


def test_healthy_false_when_errors_present(snapshot_dir):
    _write(snapshot_dir, "bad", {"key with space": "val"})
    report = check_health("bad", snapshot_dir)
    assert report.healthy is False
    assert report.errors
