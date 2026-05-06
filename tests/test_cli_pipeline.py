"""Tests for envforge.cli_pipeline."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from envforge.cli_pipeline import pipeline_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def snap_dir(tmp_path):
    return str(tmp_path)


def test_create_cmd_prints_confirmation(runner, snap_dir):
    result = runner.invoke(pipeline_group, ["create", "mypipe", "s1", "s2", "--dir", snap_dir])
    assert result.exit_code == 0
    assert "mypipe" in result.output
    assert "2 step" in result.output


def test_create_cmd_fails_on_duplicate(runner, snap_dir):
    runner.invoke(pipeline_group, ["create", "dup", "s1", "--dir", snap_dir])
    result = runner.invoke(pipeline_group, ["create", "dup", "s2", "--dir", snap_dir])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_show_cmd_lists_steps(runner, snap_dir):
    runner.invoke(pipeline_group, ["create", "show_pipe", "alpha", "beta", "--dir", snap_dir])
    result = runner.invoke(pipeline_group, ["show", "show_pipe", "--dir", snap_dir])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output


def test_show_cmd_fails_when_missing(runner, snap_dir):
    result = runner.invoke(pipeline_group, ["show", "ghost", "--dir", snap_dir])
    assert result.exit_code != 0


def test_list_cmd_shows_no_pipelines_message(runner, snap_dir):
    result = runner.invoke(pipeline_group, ["list", "--dir", snap_dir])
    assert result.exit_code == 0
    assert "No pipelines" in result.output


def test_list_cmd_shows_pipeline_names(runner, snap_dir):
    runner.invoke(pipeline_group, ["create", "pipe_a", "x", "--dir", snap_dir])
    runner.invoke(pipeline_group, ["create", "pipe_b", "y", "z", "--dir", snap_dir])
    result = runner.invoke(pipeline_group, ["list", "--dir", snap_dir])
    assert "pipe_a" in result.output
    assert "pipe_b" in result.output


def test_append_cmd_updates_step_count(runner, snap_dir):
    runner.invoke(pipeline_group, ["create", "grow", "first", "--dir", snap_dir])
    result = runner.invoke(pipeline_group, ["append", "grow", "second", "--dir", snap_dir])
    assert result.exit_code == 0
    assert "2 steps" in result.output


def test_delete_cmd_prints_deleted(runner, snap_dir):
    runner.invoke(pipeline_group, ["create", "bye", "s", "--dir", snap_dir])
    result = runner.invoke(pipeline_group, ["delete", "bye", "--dir", snap_dir])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_delete_cmd_fails_when_missing(runner, snap_dir):
    result = runner.invoke(pipeline_group, ["delete", "nope", "--dir", snap_dir])
    assert result.exit_code != 0
