"""Tests for envforge.replay."""

from __future__ import annotations

import json
import pathlib

import pytest

from envforge.replay import ReplayError, ReplayResult, replay_snapshot


@pytest.fixture()
def snapshot_dir(tmp_path: pathlib.Path) -> str:
    d = tmp_path / "snaps"
    d.mkdir()
    return str(d)


def _write(directory: str, name: str, env: dict) -> None:
    pathlib.Path(directory, f"{name}.json").write_text(json.dumps(env))


def test_replay_creates_destination(snapshot_dir: str) -> None:
    _write(snapshot_dir, "src", {"FOO": "bar"})
    replay_snapshot("src", "dst", snapshot_dir)
    assert pathlib.Path(snapshot_dir, "dst.json").exists()


def test_replay_returns_replay_result(snapshot_dir: str) -> None:
    _write(snapshot_dir, "src", {"FOO": "bar"})
    result = replay_snapshot("src", "dst", snapshot_dir)
    assert isinstance(result, ReplayResult)


def test_replay_preserves_env_by_default(snapshot_dir: str) -> None:
    env = {"A": "1", "B": "2"}
    _write(snapshot_dir, "src", env)
    result = replay_snapshot("src", "dst", snapshot_dir)
    assert result.env == env


def test_replay_raises_for_missing_source(snapshot_dir: str) -> None:
    with pytest.raises(ReplayError, match="not found"):
        replay_snapshot("missing", "dst", snapshot_dir)


def test_replay_prefix_filter_excludes_keys(snapshot_dir: str) -> None:
    _write(snapshot_dir, "src", {"APP_HOST": "localhost", "DB_URL": "postgres"})
    result = replay_snapshot("src", "dst", snapshot_dir, prefix_filter="APP_")
    assert "APP_HOST" in result.env
    assert "DB_URL" not in result.env


def test_replay_prefix_filter_records_skipped(snapshot_dir: str) -> None:
    _write(snapshot_dir, "src", {"APP_HOST": "localhost", "DB_URL": "postgres"})
    result = replay_snapshot("src", "dst", snapshot_dir, prefix_filter="APP_")
    assert "DB_URL" in result.skipped_keys


def test_replay_key_transform_applied(snapshot_dir: str) -> None:
    _write(snapshot_dir, "src", {"foo": "bar"})
    result = replay_snapshot(
        "src", "dst", snapshot_dir, key_transform=lambda k: k.upper()
    )
    assert "FOO" in result.env
    assert "foo" not in result.env


def test_replay_value_transform_applied(snapshot_dir: str) -> None:
    _write(snapshot_dir, "src", {"KEY": "hello"})
    result = replay_snapshot(
        "src", "dst", snapshot_dir, value_transform=lambda v: v.upper()
    )
    assert result.env["KEY"] == "HELLO"


def test_replay_exclude_keys(snapshot_dir: str) -> None:
    _write(snapshot_dir, "src", {"SECRET": "x", "PUBLIC": "y"})
    result = replay_snapshot("src", "dst", snapshot_dir, exclude_keys=["SECRET"])
    assert "SECRET" not in result.env
    assert "SECRET" in result.skipped_keys


def test_replay_records_transformed_keys(snapshot_dir: str) -> None:
    _write(snapshot_dir, "src", {"foo": "bar"})
    result = replay_snapshot(
        "src", "dst", snapshot_dir, key_transform=lambda k: k.upper()
    )
    assert "FOO" in result.applied_transforms


def test_replay_source_and_destination_names(snapshot_dir: str) -> None:
    _write(snapshot_dir, "alpha", {"X": "1"})
    result = replay_snapshot("alpha", "beta", snapshot_dir)
    assert result.source == "alpha"
    assert result.destination == "beta"
