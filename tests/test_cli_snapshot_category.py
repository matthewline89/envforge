"""Tests for envforge.cli_snapshot_category."""
import pytest
from pathlib import Path
from click.testing import CliRunner

from envforge.cli_snapshot_category import category_group
from envforge.snapshot_category import add_to_category


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_add_cmd_prints_confirmation(runner, snap_dir):
    result = runner.invoke(category_group, ["add", "prod", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "Added" in result.output
    assert "snap1" in result.output
    assert "prod" in result.output


def test_add_cmd_prints_already_exists(runner, snap_dir):
    add_to_category(snap_dir, "prod", "snap1")
    result = runner.invoke(category_group, ["add", "prod", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "already" in result.output


def test_remove_cmd_prints_removed(runner, snap_dir):
    add_to_category(snap_dir, "prod", "snap1")
    result = runner.invoke(category_group, ["remove", "prod", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_cmd_prints_not_found(runner, snap_dir):
    result = runner.invoke(category_group, ["remove", "prod", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_list_cmd_shows_categories(runner, snap_dir):
    add_to_category(snap_dir, "alpha", "s1")
    add_to_category(snap_dir, "beta", "s2")
    result = runner.invoke(category_group, ["list", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output


def test_list_cmd_shows_no_categories_message(runner, snap_dir):
    result = runner.invoke(category_group, ["list", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No categories" in result.output


def test_show_cmd_lists_members(runner, snap_dir):
    add_to_category(snap_dir, "prod", "snap-a")
    add_to_category(snap_dir, "prod", "snap-b")
    result = runner.invoke(category_group, ["show", "prod", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "snap-a" in result.output
    assert "snap-b" in result.output


def test_show_cmd_empty_category_message(runner, snap_dir):
    result = runner.invoke(category_group, ["show", "ghost", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "empty" in result.output or "does not exist" in result.output


def test_delete_cmd_prints_deleted(runner, snap_dir):
    add_to_category(snap_dir, "old", "snap1")
    result = runner.invoke(category_group, ["delete", "old", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "Deleted" in result.output


def test_delete_cmd_prints_not_found(runner, snap_dir):
    result = runner.invoke(category_group, ["delete", "ghost", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "does not exist" in result.output
