"""Tests for envforge.cli_snapshot_dependency."""
import json
import pytest
from click.testing import CliRunner
from pathlib import Path

from envforge.cli_snapshot_dependency import dependency_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def snap_dir(tmp_path: Path) -> str:
    return str(tmp_path)


def test_add_cmd_prints_added(runner, snap_dir):
    result = runner.invoke(
        dependency_group, ["add", "b", "a", "--dir", snap_dir]
    )
    assert result.exit_code == 0
    assert "Added dependency" in result.output
    assert "b -> a" in result.output


def test_add_cmd_prints_already_exists(runner, snap_dir):
    runner.invoke(dependency_group, ["add", "b", "a", "--dir", snap_dir])
    result = runner.invoke(
        dependency_group, ["add", "b", "a", "--dir", snap_dir]
    )
    assert "already exists" in result.output


def test_remove_cmd_prints_removed(runner, snap_dir):
    runner.invoke(dependency_group, ["add", "b", "a", "--dir", snap_dir])
    result = runner.invoke(
        dependency_group, ["remove", "b", "a", "--dir", snap_dir]
    )
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_cmd_prints_not_found(runner, snap_dir):
    result = runner.invoke(
        dependency_group, ["remove", "b", "a", "--dir", snap_dir]
    )
    assert "not found" in result.output


def test_show_cmd_prints_dependencies(runner, snap_dir):
    runner.invoke(dependency_group, ["add", "b", "a", "--dir", snap_dir])
    result = runner.invoke(
        dependency_group, ["show", "b", "--dir", snap_dir]
    )
    assert result.exit_code == 0
    assert "-> a" in result.output


def test_show_cmd_no_dependencies_message(runner, snap_dir):
    result = runner.invoke(
        dependency_group, ["show", "unknown", "--dir", snap_dir]
    )
    assert "No dependencies" in result.output


def test_list_cmd_no_dependencies_message(runner, snap_dir):
    result = runner.invoke(dependency_group, ["list", "--dir", snap_dir])
    assert "No dependencies" in result.output


def test_list_cmd_shows_all_edges(runner, snap_dir):
    runner.invoke(dependency_group, ["add", "b", "a", "--dir", snap_dir])
    runner.invoke(dependency_group, ["add", "c", "a", "--dir", snap_dir])
    result = runner.invoke(dependency_group, ["list", "--dir", snap_dir])
    assert "b -> a" in result.output
    assert "c -> a" in result.output
