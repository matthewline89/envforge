"""Tests for envforge.cli_namespace."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_namespace import namespace_group
from envforge.namespace import add_to_namespace


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def test_add_cmd_prints_confirmation(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(namespace_group, ["add", "backend", "prod", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "Added" in result.output


def test_add_cmd_prints_already_exists(runner: CliRunner, snap_dir: Path) -> None:
    add_to_namespace(snap_dir, "backend", "prod")
    result = runner.invoke(namespace_group, ["add", "backend", "prod", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "already" in result.output


def test_remove_cmd_prints_removed(runner: CliRunner, snap_dir: Path) -> None:
    add_to_namespace(snap_dir, "backend", "prod")
    result = runner.invoke(namespace_group, ["remove", "backend", "prod", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_cmd_not_found_message(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(namespace_group, ["remove", "backend", "ghost", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_list_cmd_shows_no_namespaces(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(namespace_group, ["list", "--dir", str(snap_dir)])
    assert result.exit_code == 0
    assert "No namespaces" in result.output


def test_list_cmd_shows_namespace_names(runner: CliRunner, snap_dir: Path) -> None:
    add_to_namespace(snap_dir, "frontend", "dev")
    result = runner.invoke(namespace_group, ["list", "--dir", str(snap_dir)])
    assert "frontend" in result.output


def test_show_cmd_lists_members(runner: CliRunner, snap_dir: Path) -> None:
    add_to_namespace(snap_dir, "backend", "prod")
    add_to_namespace(snap_dir, "backend", "staging")
    result = runner.invoke(namespace_group, ["show", "backend", "--dir", str(snap_dir)])
    assert "prod" in result.output
    assert "staging" in result.output


def test_show_cmd_empty_namespace(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(namespace_group, ["show", "ghost", "--dir", str(snap_dir)])
    assert "empty or does not exist" in result.output


def test_resolve_cmd_prints_namespace(runner: CliRunner, snap_dir: Path) -> None:
    add_to_namespace(snap_dir, "ops", "infra")
    result = runner.invoke(namespace_group, ["resolve", "infra", "--dir", str(snap_dir)])
    assert "ops" in result.output


def test_resolve_cmd_not_found(runner: CliRunner, snap_dir: Path) -> None:
    result = runner.invoke(namespace_group, ["resolve", "nobody", "--dir", str(snap_dir)])
    assert "does not belong" in result.output
