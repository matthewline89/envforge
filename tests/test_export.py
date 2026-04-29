"""Tests for envforge.export module."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.snapshot import save
from envforge.export import (
    export_dotenv,
    export_json,
    export_shell,
    export_yaml,
    export_snapshot,
    export_to_file,
)
from envforge.cli_export import export_group


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envforge"
    d.mkdir()
    return d


SAMPLE = {"FOO": "bar", "GREETING": 'say "hi"'}


def test_export_dotenv_contains_key():
    result = export_dotenv(SAMPLE)
    assert 'FOO="bar"' in result


def test_export_dotenv_escapes_quotes():
    result = export_dotenv(SAMPLE)
    assert 'GREETING="say \\"hi\\""' in result


def test_export_json_is_valid_json():
    result = export_json(SAMPLE)
    parsed = json.loads(result)
    assert parsed["FOO"] == "bar"


def test_export_yaml_contains_key():
    result = export_yaml(SAMPLE)
    assert "FOO:" in result


def test_export_shell_uses_export_keyword():
    result = export_shell(SAMPLE)
    assert result.startswith("export ") or "export FOO" in result


def test_export_shell_escapes_quotes():
    result = export_shell(SAMPLE)
    assert 'GREETING="say \\"hi\\""' in result


def test_export_snapshot_dotenv(snapshot_dir: Path):
    save("mysnap", {"KEY": "val"}, snapshot_dir)
    result = export_snapshot("mysnap", "dotenv", snapshot_dir)
    assert 'KEY="val"' in result


def test_export_snapshot_raises_for_missing(snapshot_dir: Path):
    with pytest.raises(FileNotFoundError):
        export_snapshot("ghost", "json", snapshot_dir)


def test_export_snapshot_raises_for_bad_format(snapshot_dir: Path):
    save("mysnap", {"K": "v"}, snapshot_dir)
    with pytest.raises(ValueError, match="Unsupported format"):
        export_snapshot("mysnap", "xml", snapshot_dir)  # type: ignore[arg-type]


def test_export_to_file_writes_content(snapshot_dir: Path, tmp_path: Path):
    save("mysnap", {"A": "1"}, snapshot_dir)
    dest = tmp_path / "out.env"
    returned = export_to_file("mysnap", "dotenv", dest, snapshot_dir)
    assert returned == dest
    assert 'A="1"' in dest.read_text()


def test_cli_run_prints_dotenv(snapshot_dir: Path):
    runner = CliRunner()
    save("mysnap", {"X": "42"}, snapshot_dir)
    result = runner.invoke(
        export_group, ["run", "mysnap", "--format", "dotenv", "--dir", str(snapshot_dir)]
    )
    assert result.exit_code == 0
    assert 'X="42"' in result.output


def test_cli_run_missing_snapshot_exits_1(snapshot_dir: Path):
    runner = CliRunner()
    result = runner.invoke(
        export_group, ["run", "nope", "--dir", str(snapshot_dir)]
    )
    assert result.exit_code == 1
