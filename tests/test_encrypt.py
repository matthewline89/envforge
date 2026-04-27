"""Tests for envforge.encrypt."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from envforge import encrypt as enc


@pytest.fixture()
def key() -> str:
    return enc.generate_key()


def test_generate_key_returns_string(key):
    assert isinstance(key, str)
    assert len(key) > 0


def test_generate_key_is_unique():
    assert enc.generate_key() != enc.generate_key()


def test_encrypt_decrypt_roundtrip(key):
    data = {"FOO": "bar", "NUM": "42"}
    ciphertext = enc.encrypt_snapshot(data, key)
    result = enc.decrypt_snapshot(ciphertext, key)
    assert result == data


def test_ciphertext_is_bytes(key):
    ciphertext = enc.encrypt_snapshot({"A": "1"}, key)
    assert isinstance(ciphertext, bytes)


def test_ciphertext_differs_from_plaintext(key):
    data = {"SECRET": "hunter2"}
    ciphertext = enc.encrypt_snapshot(data, key)
    assert json.dumps(data).encode() not in ciphertext


def test_decrypt_wrong_key_raises(key):
    ciphertext = enc.encrypt_snapshot({"X": "1"}, key)
    wrong_key = enc.generate_key()
    with pytest.raises(ValueError, match="Decryption failed"):
        enc.decrypt_snapshot(ciphertext, wrong_key)


def test_get_fernet_uses_env_var(monkeypatch, key):
    monkeypatch.setenv(enc.KEY_ENV_VAR, key)
    data = {"ENV": "var"}
    ciphertext = enc.encrypt_snapshot(data)  # no explicit key
    result = enc.decrypt_snapshot(ciphertext)  # no explicit key
    assert result == data


def test_get_fernet_raises_without_key(monkeypatch):
    monkeypatch.delenv(enc.KEY_ENV_VAR, raising=False)
    with pytest.raises(ValueError, match="No encryption key"):
        enc.encrypt_snapshot({"A": "1"})


def test_save_and_load_encrypted(tmp_path, key):
    data = {"HELLO": "world"}
    path = tmp_path / "snap.enc"
    enc.save_encrypted(data, path, key)
    assert path.exists()
    loaded = enc.load_encrypted(path, key)
    assert loaded == data


def test_load_encrypted_bad_key_raises(tmp_path, key):
    data = {"K": "v"}
    path = tmp_path / "snap.enc"
    enc.save_encrypted(data, path, key)
    wrong = enc.generate_key()
    with pytest.raises(ValueError):
        enc.load_encrypted(path, wrong)
