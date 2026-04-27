"""Tests for envforge.search module."""

from __future__ import annotations

import pytest
from pathlib import Path

from envforge.search import search_snapshots, SearchResult, SearchMatch
from envforge.snapshot import save


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


@pytest.fixture
def populated_dir(snapshot_dir: Path) -> Path:
    save("alpha", {"DATABASE_URL": "postgres://localhost/db", "DEBUG": "true"}, snapshot_dir)
    save("beta", {"API_KEY": "secret123", "DATABASE_HOST": "db.example.com"}, snapshot_dir)
    save("gamma", {"LOG_LEVEL": "INFO", "PORT": "8080"}, snapshot_dir)
    return snapshot_dir


def test_search_returns_search_result(populated_dir: Path) -> None:
    result = search_snapshots("DATABASE", populated_dir)
    assert isinstance(result, SearchResult)


def test_search_finds_key_match(populated_dir: Path) -> None:
    result = search_snapshots("DATABASE", populated_dir)
    keys = [m.key for m in result.matches]
    assert "DATABASE_URL" in keys
    assert "DATABASE_HOST" in keys


def test_search_finds_value_match(populated_dir: Path) -> None:
    result = search_snapshots("postgres", populated_dir)
    assert any(m.value == "postgres://localhost/db" for m in result.matches)


def test_search_is_empty_when_no_match(populated_dir: Path) -> None:
    result = search_snapshots("NONEXISTENT_XYZ", populated_dir)
    assert result.is_empty()


def test_search_case_insensitive_by_default(populated_dir: Path) -> None:
    result = search_snapshots("debug", populated_dir)
    assert any(m.key == "DEBUG" for m in result.matches)


def test_search_case_sensitive_excludes_wrong_case(populated_dir: Path) -> None:
    result = search_snapshots("debug", populated_dir, case_sensitive=True)
    assert result.is_empty()


def test_search_keys_only_skips_value_matches(populated_dir: Path) -> None:
    result = search_snapshots("true", populated_dir, search_keys=True, search_values=False)
    assert all("true" in m.key.lower() for m in result.matches)


def test_search_values_only_skips_key_matches(populated_dir: Path) -> None:
    result = search_snapshots("PORT", populated_dir, search_keys=False, search_values=True)
    assert all("PORT" in m.value.upper() for m in result.matches)


def test_search_limited_to_single_snapshot(populated_dir: Path) -> None:
    result = search_snapshots("DATABASE", populated_dir, snapshot_name="alpha")
    assert all(m.snapshot_name == "alpha" for m in result.matches)


def test_grouped_by_snapshot(populated_dir: Path) -> None:
    result = search_snapshots("DATABASE", populated_dir)
    grouped = result.grouped_by_snapshot()
    assert "alpha" in grouped
    assert "beta" in grouped


def test_invalid_regex_raises_value_error(populated_dir: Path) -> None:
    with pytest.raises(ValueError, match="Invalid regex pattern"):
        search_snapshots("[invalid", populated_dir)


def test_missing_snapshot_is_skipped(snapshot_dir: Path) -> None:
    result = search_snapshots("anything", snapshot_dir, snapshot_name="ghost")
    assert result.is_empty()
