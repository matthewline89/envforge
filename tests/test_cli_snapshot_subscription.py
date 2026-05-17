"""Tests for envforge.cli_snapshot_subscription."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_snapshot_subscription import subscription_group
from envforge.snapshot_subscription import subscribe


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_add_cmd_prints_subscribed(runner, snap_dir):
    result = runner.invoke(
        subscription_group, ["add", "alpha", "--dir", str(snap_dir)]
    )
    assert result.exit_code == 0
    assert "Subscribed 'alpha'" in result.output


def test_add_cmd_prints_updated_on_duplicate(runner, snap_dir):
    subscribe(snap_dir, "alpha")
    result = runner.invoke(
        subscription_group, ["add", "alpha", "--dir", str(snap_dir)]
    )
    assert "Updated subscription" in result.output


def test_add_cmd_respects_event_option(runner, snap_dir):
    result = runner.invoke(
        subscription_group,
        ["add", "alpha", "--event", "save", "--dir", str(snap_dir)],
    )
    assert "save" in result.output


def test_remove_cmd_prints_removed(runner, snap_dir):
    subscribe(snap_dir, "alpha")
    result = runner.invoke(
        subscription_group, ["remove", "alpha", "--dir", str(snap_dir)]
    )
    assert "Removed" in result.output


def test_remove_cmd_prints_not_found(runner, snap_dir):
    result = runner.invoke(
        subscription_group, ["remove", "ghost", "--dir", str(snap_dir)]
    )
    assert "No subscription found" in result.output


def test_list_cmd_shows_no_subscriptions_message(runner, snap_dir):
    result = runner.invoke(
        subscription_group, ["list", "--dir", str(snap_dir)]
    )
    assert "No subscriptions" in result.output


def test_list_cmd_shows_subscriptions(runner, snap_dir):
    subscribe(snap_dir, "alpha", event="save", label="lbl")
    result = runner.invoke(
        subscription_group, ["list", "--dir", str(snap_dir)]
    )
    assert "alpha" in result.output
    assert "save" in result.output
    assert "lbl" in result.output
