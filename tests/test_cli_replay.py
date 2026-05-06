"""CLI tests for the replay command group."""

from __future__ import annotations

import json
import pathlib

import pytest
from click.testing import CliRunner

from envforge.cli_replay import replay_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def snap_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    d = tmp_path / "snaps"
    d.mkdir()
    return d


def _write(directory: pathlib.Path, name: str, env: dict) -> None:
    (directory / f"{name}.json").write_text(json.dumps(env))


def test_run_shows_source_and_destination(runner: CliRunner, snap_dir: pathlib.Path) -> None:
    _write(snap_dir, "src", {"FOO": "bar"})
    result = runner.invoke(
        replay_group, ["run", "src", "dst", "--dir", str(snap_dir)]
    )
    assert result.exit_code == 0
    assert "src" in result.output
    assert "dst" in result.output


def test_run_reports_key_counts(runner: CliRunner, snap_dir: pathlib.Path) -> None:
    _write(snap_dir, "src", {"A": "1", "B": "2"})
    result = runner.invoke(
        replay_group, ["run", "src", "dst", "--dir", str(snap_dir)]
    )
    assert "2" in result.output


def test_run_fails_for_missing_snapshot(runner: CliRunner, snap_dir: pathlib.Path) -> None:
    result = runner.invoke(
        replay_group, ["run", "ghost", "dst", "--dir", str(snap_dir)]
    )
    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "Error" in result.output


def test_run_upper_keys_flag(runner: CliRunner, snap_dir: pathlib.Path) -> None:
    _write(snap_dir, "src", {"foo": "bar"})
    runner.invoke(
        replay_group,
        ["run", "src", "dst", "--dir", str(snap_dir), "--upper-keys"],
    )
    saved = json.loads((snap_dir / "dst.json").read_text())
    assert "FOO" in saved


def test_run_prefix_filter(runner: CliRunner, snap_dir: pathlib.Path) -> None:
    _write(snap_dir, "src", {"APP_KEY": "v", "DB_URL": "u"})
    runner.invoke(
        replay_group,
        ["run", "src", "dst", "--dir", str(snap_dir), "--prefix", "APP_"],
    )
    saved = json.loads((snap_dir / "dst.json").read_text())
    assert "APP_KEY" in saved
    assert "DB_URL" not in saved


def test_run_exclude_option(runner: CliRunner, snap_dir: pathlib.Path) -> None:
    _write(snap_dir, "src", {"SECRET": "s", "PUBLIC": "p"})
    runner.invoke(
        replay_group,
        ["run", "src", "dst", "--dir", str(snap_dir), "--exclude", "SECRET"],
    )
    saved = json.loads((snap_dir / "dst.json").read_text())
    assert "SECRET" not in saved
    assert "PUBLIC" in saved
