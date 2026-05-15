"""Tests for envforge.snapshot_preview."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_preview import (
    PreviewLine,
    SnapshotPreview,
    format_preview,
    preview_snapshot,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


def test_preview_returns_snapshot_preview(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "mysnap", {"FOO": "bar"})
    result = preview_snapshot("mysnap", snapshot_dir)
    assert isinstance(result, SnapshotPreview)


def test_preview_name_matches(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "mysnap", {"FOO": "bar"})
    result = preview_snapshot("mysnap", snapshot_dir)
    assert result.name == "mysnap"


def test_preview_contains_all_keys(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "mysnap", {"A": "1", "B": "2", "C": "3"})
    result = preview_snapshot("mysnap", snapshot_dir)
    assert len(result) == 3


def test_preview_masks_secret_key(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "mysnap", {"API_TOKEN": "supersecret"})
    result = preview_snapshot("mysnap", snapshot_dir, mask_secrets=True)
    line = result.lines[0]
    assert line.masked is True
    assert line.display_value() != "supersecret"


def test_preview_no_mask_shows_value(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "mysnap", {"API_TOKEN": "supersecret"})
    result = preview_snapshot("mysnap", snapshot_dir, mask_secrets=False)
    line = result.lines[0]
    assert line.masked is False
    assert line.display_value() == "supersecret"


def test_preview_limit_truncates(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "mysnap", {"A": "1", "B": "2", "C": "3"})
    result = preview_snapshot("mysnap", snapshot_dir, limit=2)
    assert len(result) == 2
    assert result.truncated is True


def test_preview_no_truncation_when_within_limit(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "mysnap", {"A": "1", "B": "2"})
    result = preview_snapshot("mysnap", snapshot_dir, limit=10)
    assert result.truncated is False


def test_preview_key_filter_matches_substring(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "mysnap", {"DATABASE_URL": "x", "FOO": "y"})
    result = preview_snapshot("mysnap", snapshot_dir, key_filter="database")
    assert len(result) == 1
    assert result.lines[0].key == "DATABASE_URL"


def test_format_preview_contains_key_and_value(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "mysnap", {"FOO": "bar"})
    result = preview_snapshot("mysnap", snapshot_dir, mask_secrets=False)
    text = format_preview(result)
    assert "FOO=bar" in text


def test_format_preview_with_index(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "mysnap", {"FOO": "bar"})
    result = preview_snapshot("mysnap", snapshot_dir, mask_secrets=False)
    text = format_preview(result, show_index=True)
    assert "1" in text


def test_format_preview_truncated_note(snapshot_dir: Path) -> None:
    _write(snapshot_dir, "mysnap", {"A": "1", "B": "2", "C": "3"})
    result = preview_snapshot("mysnap", snapshot_dir, limit=1)
    text = format_preview(result)
    assert "truncated" in text
