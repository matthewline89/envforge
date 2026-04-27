"""Tests for envforge.cli_encrypt CLI commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge import encrypt as enc
from envforge.cli_encrypt import encrypt_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def key():
    return enc.generate_key()


@pytest.fixture()
def snap_dir(tmp_path):
    return str(tmp_path)


def test_keygen_prints_key(runner):
    result = runner.invoke(encrypt_group, ["keygen"])
    assert result.exit_code == 0
    key_line = result.output.strip().splitlines()[0]
    # Should be a valid Fernet key (base64, 44 chars)
    assert len(key_line) == 44


def test_save_creates_enc_file(runner, snap_dir, key, monkeypatch):
    monkeypatch.setenv("PATH", "/usr/bin")
    result = runner.invoke(
        encrypt_group,
        ["save", "mysnap", "--dir", snap_dir, "--key", key],
    )
    assert result.exit_code == 0, result.output
    assert (Path(snap_dir) / "mysnap.enc").exists()


def test_save_output_mentions_path(runner, snap_dir, key):
    result = runner.invoke(
        encrypt_group,
        ["save", "proj", "--dir", snap_dir, "--key", key],
    )
    assert "proj.enc" in result.output


def test_load_prints_json(runner, snap_dir, key):
    # First save
    runner.invoke(encrypt_group, ["save", "s1", "--dir", snap_dir, "--key", key])
    result = runner.invoke(
        encrypt_group,
        ["load", "s1", "--dir", snap_dir, "--key", key],
    )
    assert result.exit_code == 0, result.output
    import json
    data = json.loads(result.output)
    assert isinstance(data, dict)


def test_load_with_out_saves_plain_snapshot(runner, snap_dir, key):
    runner.invoke(encrypt_group, ["save", "enc1", "--dir", snap_dir, "--key", key])
    result = runner.invoke(
        encrypt_group,
        ["load", "enc1", "--dir", snap_dir, "--key", key, "--out", "plain1"],
    )
    assert result.exit_code == 0
    assert (Path(snap_dir) / "plain1.json").exists()


def test_load_missing_snapshot_errors(runner, snap_dir, key):
    result = runner.invoke(
        encrypt_group,
        ["load", "ghost", "--dir", snap_dir, "--key", key],
    )
    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "Error" in result.output


def test_load_wrong_key_errors(runner, snap_dir, key):
    runner.invoke(encrypt_group, ["save", "s2", "--dir", snap_dir, "--key", key])
    wrong = enc.generate_key()
    result = runner.invoke(
        encrypt_group,
        ["load", "s2", "--dir", snap_dir, "--key", wrong],
    )
    assert result.exit_code != 0
