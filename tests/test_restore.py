"""Tests for envforge.restore module."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from envforge.restore import (
    apply_to_current_process,
    generate_export_script,
    restore_to_file,
)
from envforge.snapshot import save


SAMPLE_ENV = {"APP_ENV": "production", "DB_URL": 'postgres://user:p@ss"word@host/db', "PORT": "8080"}


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


# --- generate_export_script ---

def test_generate_bash_script_contains_exports():
    script = generate_export_script({"FOO": "bar"}, shell="bash")
    assert 'export FOO="bar"' in script


def test_generate_bash_script_has_shebang():
    script = generate_export_script({"X": "1"}, shell="bash")
    assert script.startswith("#!/usr/bin/env bash")


def test_generate_zsh_script_has_shebang():
    script = generate_export_script({"X": "1"}, shell="zsh")
    assert script.startswith("#!/usr/bin/env zsh")


def test_generate_fish_script_uses_set_x():
    script = generate_export_script({"FOO": "bar"}, shell="fish")
    assert 'set -x FOO "bar"' in script
    assert "export" not in script


def test_generate_env_format_no_export_keyword():
    script = generate_export_script({"FOO": "bar"}, shell="env")
    assert "FOO=bar" in script
    assert "export" not in script


def test_generate_script_escapes_double_quotes():
    script = generate_export_script({"DB": 'pass"word'}, shell="bash")
    assert '\\"' in script


def test_generate_script_unsupported_shell_raises():
    with pytest.raises(ValueError, match="Unsupported shell format"):
        generate_export_script({"X": "1"}, shell="powershell")


# --- restore_to_file ---

def test_restore_to_file_creates_script(tmp_path, snapshot_dir):
    save("prod", SAMPLE_ENV, snapshot_dir=snapshot_dir)
    out = tmp_path / "restore.sh"
    restore_to_file("prod", out, shell="bash", snapshot_dir=snapshot_dir)
    assert out.exists()
    content = out.read_text()
    assert 'export PORT="8080"' in content


def test_restore_to_file_returns_env_dict(tmp_path, snapshot_dir):
    save("dev", {"ENV": "dev"}, snapshot_dir=snapshot_dir)
    out = tmp_path / "restore.sh"
    result = restore_to_file("dev", out, snapshot_dir=snapshot_dir)
    assert result == {"ENV": "dev"}


# --- apply_to_current_process ---

def test_apply_to_current_process_sets_env(snapshot_dir, monkeypatch):
    save("local", {"MY_VAR": "hello"}, snapshot_dir=snapshot_dir)
    monkeypatch.delenv("MY_VAR", raising=False)
    applied = apply_to_current_process("local", snapshot_dir=snapshot_dir)
    assert os.environ["MY_VAR"] == "hello"
    assert "MY_VAR" in applied


def test_apply_skips_existing_without_overwrite(snapshot_dir, monkeypatch):
    save("local", {"MY_VAR": "new_value"}, snapshot_dir=snapshot_dir)
    monkeypatch.setenv("MY_VAR", "original")
    apply_to_current_process("local", snapshot_dir=snapshot_dir, overwrite=False)
    assert os.environ["MY_VAR"] == "original"


def test_apply_overwrites_existing_when_flag_set(snapshot_dir, monkeypatch):
    save("local", {"MY_VAR": "new_value"}, snapshot_dir=snapshot_dir)
    monkeypatch.setenv("MY_VAR", "original")
    apply_to_current_process("local", snapshot_dir=snapshot_dir, overwrite=True)
    assert os.environ["MY_VAR"] == "new_value"
