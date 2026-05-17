"""Tests for envforge.snapshot_dependency."""
import pytest
from pathlib import Path

from envforge.snapshot_dependency import (
    add_dependency,
    remove_dependency,
    get_report,
    DependencyReport,
    DependencyEntry,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_add_dependency_creates_file(snapshot_dir):
    add_dependency(snapshot_dir, "b", "a")
    assert (snapshot_dir / "dependencies.json").exists()


def test_add_dependency_returns_true_when_new(snapshot_dir):
    result = add_dependency(snapshot_dir, "b", "a")
    assert result is True


def test_add_dependency_returns_false_when_duplicate(snapshot_dir):
    add_dependency(snapshot_dir, "b", "a")
    result = add_dependency(snapshot_dir, "b", "a")
    assert result is False


def test_add_dependency_stores_edge(snapshot_dir):
    add_dependency(snapshot_dir, "b", "a")
    report = get_report(snapshot_dir)
    entry = report.for_snapshot("b")
    assert entry is not None
    assert "a" in entry.depends_on


def test_add_dependency_stores_note(snapshot_dir):
    add_dependency(snapshot_dir, "b", "a", note="needs base vars")
    report = get_report(snapshot_dir)
    assert report.for_snapshot("b").note == "needs base vars"


def test_add_multiple_dependencies(snapshot_dir):
    add_dependency(snapshot_dir, "c", "a")
    add_dependency(snapshot_dir, "c", "b")
    report = get_report(snapshot_dir)
    entry = report.for_snapshot("c")
    assert "a" in entry.depends_on
    assert "b" in entry.depends_on


def test_remove_dependency_returns_true_when_found(snapshot_dir):
    add_dependency(snapshot_dir, "b", "a")
    result = remove_dependency(snapshot_dir, "b", "a")
    assert result is True


def test_remove_dependency_removes_edge(snapshot_dir):
    add_dependency(snapshot_dir, "b", "a")
    remove_dependency(snapshot_dir, "b", "a")
    report = get_report(snapshot_dir)
    entry = report.for_snapshot("b")
    assert entry is None or "a" not in entry.depends_on


def test_remove_dependency_returns_false_when_missing(snapshot_dir):
    result = remove_dependency(snapshot_dir, "b", "a")
    assert result is False


def test_get_report_returns_dependency_report(snapshot_dir):
    report = get_report(snapshot_dir)
    assert isinstance(report, DependencyReport)


def test_report_is_empty_when_no_deps(snapshot_dir):
    report = get_report(snapshot_dir)
    assert report.is_empty()


def test_report_not_empty_after_add(snapshot_dir):
    add_dependency(snapshot_dir, "b", "a")
    report = get_report(snapshot_dir)
    assert not report.is_empty()


def test_dependents_of_returns_correct_snapshots(snapshot_dir):
    add_dependency(snapshot_dir, "b", "a")
    add_dependency(snapshot_dir, "c", "a")
    report = get_report(snapshot_dir)
    dependents = report.dependents_of("a")
    assert "b" in dependents
    assert "c" in dependents


def test_dependents_of_excludes_unrelated(snapshot_dir):
    add_dependency(snapshot_dir, "b", "a")
    add_dependency(snapshot_dir, "c", "d")
    report = get_report(snapshot_dir)
    dependents = report.dependents_of("a")
    assert "c" not in dependents
