"""Tests for envforge.snapshot_workflow."""
from __future__ import annotations

import pytest
from pathlib import Path

from envforge.snapshot_workflow import (
    WorkflowError,
    append_step,
    create_workflow,
    delete_workflow,
    get_workflow,
    list_workflows,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envforge"
    d.mkdir()
    return d


def test_create_workflow_creates_file(snapshot_dir: Path) -> None:
    create_workflow(snapshot_dir, "deploy")
    assert (snapshot_dir / "workflows.json").exists()


def test_create_workflow_returns_true_when_new(snapshot_dir: Path) -> None:
    assert create_workflow(snapshot_dir, "deploy") is True


def test_create_workflow_returns_false_when_overwritten(snapshot_dir: Path) -> None:
    create_workflow(snapshot_dir, "deploy")
    assert create_workflow(snapshot_dir, "deploy") is False


def test_create_workflow_stores_description(snapshot_dir: Path) -> None:
    create_workflow(snapshot_dir, "ci", description="CI pipeline")
    wf = get_workflow(snapshot_dir, "ci")
    assert wf.description == "CI pipeline"


def test_create_workflow_starts_with_no_steps(snapshot_dir: Path) -> None:
    create_workflow(snapshot_dir, "empty")
    wf = get_workflow(snapshot_dir, "empty")
    assert wf.steps == []


def test_append_step_adds_step(snapshot_dir: Path) -> None:
    create_workflow(snapshot_dir, "w1")
    append_step(snapshot_dir, "w1", "capture")
    wf = get_workflow(snapshot_dir, "w1")
    assert len(wf.steps) == 1
    assert wf.steps[0].operation == "capture"


def test_append_step_stores_params(snapshot_dir: Path) -> None:
    create_workflow(snapshot_dir, "w2")
    append_step(snapshot_dir, "w2", "export", {"format": "dotenv"})
    wf = get_workflow(snapshot_dir, "w2")
    assert wf.steps[0].params == {"format": "dotenv"}


def test_append_step_raises_when_workflow_missing(snapshot_dir: Path) -> None:
    with pytest.raises(WorkflowError):
        append_step(snapshot_dir, "ghost", "capture")


def test_append_multiple_steps_ordered(snapshot_dir: Path) -> None:
    create_workflow(snapshot_dir, "multi")
    append_step(snapshot_dir, "multi", "capture")
    append_step(snapshot_dir, "multi", "prune")
    wf = get_workflow(snapshot_dir, "multi")
    assert [s.operation for s in wf.steps] == ["capture", "prune"]


def test_get_workflow_raises_when_missing(snapshot_dir: Path) -> None:
    with pytest.raises(WorkflowError):
        get_workflow(snapshot_dir, "nope")


def test_list_workflows_returns_empty_when_none(snapshot_dir: Path) -> None:
    assert list_workflows(snapshot_dir) == []


def test_list_workflows_returns_names(snapshot_dir: Path) -> None:
    create_workflow(snapshot_dir, "a")
    create_workflow(snapshot_dir, "b")
    names = list_workflows(snapshot_dir)
    assert set(names) == {"a", "b"}


def test_delete_workflow_returns_true_when_found(snapshot_dir: Path) -> None:
    create_workflow(snapshot_dir, "del_me")
    assert delete_workflow(snapshot_dir, "del_me") is True


def test_delete_workflow_returns_false_when_missing(snapshot_dir: Path) -> None:
    assert delete_workflow(snapshot_dir, "ghost") is False


def test_delete_workflow_removes_from_list(snapshot_dir: Path) -> None:
    create_workflow(snapshot_dir, "gone")
    delete_workflow(snapshot_dir, "gone")
    assert "gone" not in list_workflows(snapshot_dir)
