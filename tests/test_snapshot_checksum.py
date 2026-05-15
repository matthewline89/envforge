"""Tests for envforge.snapshot_checksum."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_checksum import (
    ChecksumEntry,
    ChecksumVerifyResult,
    list_checksums,
    record_checksum,
    remove_checksum,
    verify_checksum,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


def test_record_checksum_creates_checksums_file(snapshot_dir):
    _write(snapshot_dir, "dev", {"FOO": "bar"})
    record_checksum("dev", snapshot_dir)
    assert (snapshot_dir / "checksums.json").exists()


def test_record_checksum_returns_entry(snapshot_dir):
    _write(snapshot_dir, "dev", {"FOO": "bar"})
    entry = record_checksum("dev", snapshot_dir)
    assert isinstance(entry, ChecksumEntry)
    assert entry.name == "dev"
    assert len(entry.checksum) == 64  # sha256 hex


def test_record_checksum_stores_algorithm(snapshot_dir):
    _write(snapshot_dir, "dev", {"FOO": "bar"})
    entry = record_checksum("dev", snapshot_dir, algorithm="sha256")
    assert entry.algorithm == "sha256"


def test_verify_checksum_returns_none_when_not_recorded(snapshot_dir):
    _write(snapshot_dir, "dev", {"FOO": "bar"})
    result = verify_checksum("dev", snapshot_dir)
    assert result is None


def test_verify_checksum_ok_when_unchanged(snapshot_dir):
    _write(snapshot_dir, "dev", {"FOO": "bar"})
    record_checksum("dev", snapshot_dir)
    result = verify_checksum("dev", snapshot_dir)
    assert isinstance(result, ChecksumVerifyResult)
    assert result.ok is True


def test_verify_checksum_fails_when_env_mutated(snapshot_dir):
    _write(snapshot_dir, "dev", {"FOO": "bar"})
    record_checksum("dev", snapshot_dir)
    # mutate the snapshot on disk
    _write(snapshot_dir, "dev", {"FOO": "CHANGED"})
    result = verify_checksum("dev", snapshot_dir)
    assert result is not None
    assert result.ok is False
    assert result.expected != result.actual


def test_verify_checksum_result_has_name(snapshot_dir):
    _write(snapshot_dir, "prod", {"DB": "postgres"})
    record_checksum("prod", snapshot_dir)
    result = verify_checksum("prod", snapshot_dir)
    assert result.name == "prod"


def test_remove_checksum_returns_true_when_found(snapshot_dir):
    _write(snapshot_dir, "dev", {"A": "1"})
    record_checksum("dev", snapshot_dir)
    assert remove_checksum("dev", snapshot_dir) is True


def test_remove_checksum_returns_false_when_missing(snapshot_dir):
    assert remove_checksum("ghost", snapshot_dir) is False


def test_remove_checksum_deletes_entry(snapshot_dir):
    _write(snapshot_dir, "dev", {"A": "1"})
    record_checksum("dev", snapshot_dir)
    remove_checksum("dev", snapshot_dir)
    assert verify_checksum("dev", snapshot_dir) is None


def test_list_checksums_returns_empty_when_none(snapshot_dir):
    assert list_checksums(snapshot_dir) == []


def test_list_checksums_returns_all_entries(snapshot_dir):
    _write(snapshot_dir, "dev", {"A": "1"})
    _write(snapshot_dir, "prod", {"B": "2"})
    record_checksum("dev", snapshot_dir)
    record_checksum("prod", snapshot_dir)
    entries = list_checksums(snapshot_dir)
    names = {e.name for e in entries}
    assert names == {"dev", "prod"}


def test_checksum_is_stable_across_calls(snapshot_dir):
    _write(snapshot_dir, "dev", {"FOO": "bar", "BAZ": "qux"})
    e1 = record_checksum("dev", snapshot_dir)
    e2 = record_checksum("dev", snapshot_dir)
    assert e1.checksum == e2.checksum
