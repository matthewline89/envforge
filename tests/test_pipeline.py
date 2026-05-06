"""Tests for envforge.pipeline."""
import pytest
from pathlib import Path
from envforge.pipeline import (
    create_pipeline,
    get_pipeline,
    list_pipelines,
    delete_pipeline,
    append_step,
    Pipeline,
    PipelineError,
)


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path


def test_create_pipeline_returns_pipeline(snapshot_dir):
    p = create_pipeline(snapshot_dir, "deploy", ["base", "prod"])
    assert isinstance(p, Pipeline)
    assert p.name == "deploy"


def test_create_pipeline_stores_steps(snapshot_dir):
    p = create_pipeline(snapshot_dir, "ci", ["lint", "test", "build"])
    assert p.steps == ["lint", "test", "build"]


def test_create_pipeline_stores_description(snapshot_dir):
    p = create_pipeline(snapshot_dir, "ci", ["s1"], description="CI pipeline")
    assert p.description == "CI pipeline"


def test_create_pipeline_raises_when_duplicate(snapshot_dir):
    create_pipeline(snapshot_dir, "dup", ["a"])
    with pytest.raises(PipelineError, match="already exists"):
        create_pipeline(snapshot_dir, "dup", ["b"])


def test_create_pipeline_writes_json_file(snapshot_dir):
    create_pipeline(snapshot_dir, "mypipe", ["snap1"])
    assert (snapshot_dir / "pipelines.json").exists()


def test_get_pipeline_returns_correct_pipeline(snapshot_dir):
    create_pipeline(snapshot_dir, "alpha", ["x", "y"])
    p = get_pipeline(snapshot_dir, "alpha")
    assert p.steps == ["x", "y"]


def test_get_pipeline_raises_when_missing(snapshot_dir):
    with pytest.raises(PipelineError, match="not found"):
        get_pipeline(snapshot_dir, "ghost")


def test_list_pipelines_returns_empty_list(snapshot_dir):
    result = list_pipelines(snapshot_dir)
    assert result == []


def test_list_pipelines_returns_all(snapshot_dir):
    create_pipeline(snapshot_dir, "p1", ["a"])
    create_pipeline(snapshot_dir, "p2", ["b", "c"])
    result = list_pipelines(snapshot_dir)
    names = [p.name for p in result]
    assert "p1" in names
    assert "p2" in names


def test_delete_pipeline_returns_true_when_found(snapshot_dir):
    create_pipeline(snapshot_dir, "del_me", ["s"])
    assert delete_pipeline(snapshot_dir, "del_me") is True


def test_delete_pipeline_returns_false_when_missing(snapshot_dir):
    assert delete_pipeline(snapshot_dir, "nope") is False


def test_delete_pipeline_removes_from_list(snapshot_dir):
    create_pipeline(snapshot_dir, "gone", ["s"])
    delete_pipeline(snapshot_dir, "gone")
    assert all(p.name != "gone" for p in list_pipelines(snapshot_dir))


def test_append_step_adds_to_end(snapshot_dir):
    create_pipeline(snapshot_dir, "pipe", ["first"])
    p = append_step(snapshot_dir, "pipe", "second")
    assert p.steps == ["first", "second"]


def test_append_step_raises_when_pipeline_missing(snapshot_dir):
    with pytest.raises(PipelineError, match="not found"):
        append_step(snapshot_dir, "none", "snap")
