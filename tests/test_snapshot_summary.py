"""Tests for envforge.snapshot_summary."""
import json
from pathlib import Path

import pytest

from envforge.snapshot_summary import summarize, format_summary, SnapshotSummary


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env))


def test_summarize_returns_snapshot_summary(snapshot_dir):
    _write(snapshot_dir, "mysnap", {"FOO": "bar", "BAZ": "qux"})
    result = summarize(snapshot_dir, "mysnap")
    assert isinstance(result, SnapshotSummary)


def test_summarize_total_keys(snapshot_dir):
    _write(snapshot_dir, "s1", {"A": "1", "B": "2", "C": "3"})
    result = summarize(snapshot_dir, "s1")
    assert result.total_keys == 3


def test_summarize_name_matches(snapshot_dir):
    _write(snapshot_dir, "named", {"X": "y"})
    result = summarize(snapshot_dir, "named")
    assert result.name == "named"


def test_summarize_counts_empty_values(snapshot_dir):
    _write(snapshot_dir, "empties", {"A": "", "B": "", "C": "ok"})
    result = summarize(snapshot_dir, "empties")
    assert result.empty_values == 2


def test_summarize_no_annotation_by_default(snapshot_dir):
    _write(snapshot_dir, "clean", {"K": "v"})
    result = summarize(snapshot_dir, "clean")
    assert result.annotation is None


def test_summarize_not_locked_by_default(snapshot_dir):
    _write(snapshot_dir, "unlocked", {"K": "v"})
    result = summarize(snapshot_dir, "unlocked")
    assert result.is_locked is False


def test_summarize_sample_keys_at_most_five(snapshot_dir):
    env = {f"KEY_{i}": str(i) for i in range(10)}
    _write(snapshot_dir, "big", env)
    result = summarize(snapshot_dir, "big")
    assert len(result.sample_keys) <= 5


def test_summarize_sample_keys_sorted(snapshot_dir):
    _write(snapshot_dir, "sorted", {"Z": "1", "A": "2", "M": "3"})
    result = summarize(snapshot_dir, "sorted")
    assert result.sample_keys == sorted(result.sample_keys)


def test_format_summary_contains_name(snapshot_dir):
    _write(snapshot_dir, "fmtsnap", {"FOO": "bar"})
    s = summarize(snapshot_dir, "fmtsnap")
    text = format_summary(s)
    assert "fmtsnap" in text


def test_format_summary_contains_key_count(snapshot_dir):
    _write(snapshot_dir, "kcount", {"A": "1", "B": "2"})
    s = summarize(snapshot_dir, "kcount")
    text = format_summary(s)
    assert "2" in text


def test_format_summary_shows_none_annotation(snapshot_dir):
    _write(snapshot_dir, "noanno", {"X": "y"})
    s = summarize(snapshot_dir, "noanno")
    text = format_summary(s)
    assert "(none)" in text


def test_format_summary_shows_locked_no(snapshot_dir):
    _write(snapshot_dir, "notlocked", {"X": "y"})
    s = summarize(snapshot_dir, "notlocked")
    text = format_summary(s)
    assert "no" in text
