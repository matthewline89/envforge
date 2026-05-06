"""CLI tests for the label commands."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_label import label_group
from envforge.label import add_label


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_add_cmd_prints_confirmation(runner, snap_dir):
    result = runner.invoke(
        label_group, ["add", "snap1", "production", "--dir", str(snap_dir)]
    )
    assert result.exit_code == 0
    assert "added" in result.output


def test_add_cmd_prints_already_exists(runner, snap_dir):
    add_label(snap_dir, "snap1", "production")
    result = runner.invoke(
        label_group, ["add", "snap1", "production", "--dir", str(snap_dir)]
    )
    assert result.exit_code == 0
    assert "already exists" in result.output


def test_remove_cmd_prints_removed(runner, snap_dir):
    add_label(snap_dir, "snap1", "old")
    result = runner.invoke(
        label_group, ["remove", "snap1", "old", "--dir", str(snap_dir)]
    )
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_cmd_prints_not_found(runner, snap_dir):
    result = runner.invoke(
        label_group, ["remove", "snap1", "ghost", "--dir", str(snap_dir)]
    )
    assert result.exit_code == 0
    assert "not found" in result.output


def test_show_cmd_prints_labels(runner, snap_dir):
    add_label(snap_dir, "snap1", "ci")
    add_label(snap_dir, "snap1", "stable")
    result = runner.invoke(label_group, ["show", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "ci" in result.output
    assert "stable" in result.output


def test_show_cmd_no_labels_message(runner, snap_dir):
    result = runner.invoke(label_group, ["show", "snap1", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No labels" in result.output


def test_find_cmd_lists_matching_snapshots(runner, snap_dir):
    add_label(snap_dir, "snap1", "deploy")
    add_label(snap_dir, "snap2", "deploy")
    result = runner.invoke(label_group, ["find", "deploy", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "snap1" in result.output
    assert "snap2" in result.output


def test_list_cmd_shows_no_labels_message(runner, snap_dir):
    result = runner.invoke(label_group, ["list", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No labels" in result.output


def test_list_cmd_shows_all_mappings(runner, snap_dir):
    add_label(snap_dir, "snap1", "a")
    add_label(snap_dir, "snap2", "b")
    result = runner.invoke(label_group, ["list", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "snap1" in result.output
    assert "snap2" in result.output
