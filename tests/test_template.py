"""Tests for envforge.template."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge import template as tmpl


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def test_create_template_writes_file(snapshot_dir: Path) -> None:
    tmpl.create_template({"DB_URL": "postgres://localhost"}, snapshot_dir, "myapp")
    assert _template_file(snapshot_dir, "myapp").exists()


def test_create_template_uses_placeholders(snapshot_dir: Path) -> None:
    tmpl.create_template({"API_KEY": "secret", "PORT": "8080"}, snapshot_dir, "svc")
    data = json.loads(_template_file(snapshot_dir, "svc").read_text())
    assert data["API_KEY"] == "{{ API_KEY }}"
    assert data["PORT"] == "{{ PORT }}"


def test_load_template_returns_dict(snapshot_dir: Path) -> None:
    tmpl.create_template({"FOO": "bar"}, snapshot_dir, "t1")
    data = tmpl.load_template(snapshot_dir, "t1")
    assert isinstance(data, dict)
    assert "FOO" in data


def test_load_template_raises_for_missing(snapshot_dir: Path) -> None:
    snapshot_dir.mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        tmpl.load_template(snapshot_dir, "nonexistent")


def test_list_templates_empty(snapshot_dir: Path) -> None:
    snapshot_dir.mkdir(parents=True)
    assert tmpl.list_templates(snapshot_dir) == []


def test_list_templates_returns_names(snapshot_dir: Path) -> None:
    tmpl.create_template({"A": "1"}, snapshot_dir, "alpha")
    tmpl.create_template({"B": "2"}, snapshot_dir, "beta")
    names = tmpl.list_templates(snapshot_dir)
    assert "alpha" in names
    assert "beta" in names


def test_apply_template_resolves_placeholders() -> None:
    template = {"DB_HOST": "{{ DB_HOST }}", "PORT": "{{ PORT }}"}
    result = tmpl.apply_template(template, {"DB_HOST": "localhost", "PORT": "5432"})
    assert result == {"DB_HOST": "localhost", "PORT": "5432"}


def test_apply_template_raises_on_missing_value() -> None:
    template = {"SECRET": "{{ SECRET }}"}
    with pytest.raises(KeyError, match="SECRET"):
        tmpl.apply_template(template, {})


def test_apply_template_keeps_literal_values() -> None:
    template = {"STATIC": "hardcoded", "DYN": "{{ DYN }}"}
    result = tmpl.apply_template(template, {"DYN": "dynamic"})
    assert result["STATIC"] == "hardcoded"
    assert result["DYN"] == "dynamic"


def test_delete_template_removes_file(snapshot_dir: Path) -> None:
    tmpl.create_template({"X": "1"}, snapshot_dir, "to_delete")
    assert tmpl.delete_template(snapshot_dir, "to_delete") is True
    assert not _template_file(snapshot_dir, "to_delete").exists()


def test_delete_template_returns_false_when_missing(snapshot_dir: Path) -> None:
    snapshot_dir.mkdir(parents=True)
    assert tmpl.delete_template(snapshot_dir, "ghost") is False


def _template_file(snapshot_dir: Path, name: str) -> Path:
    return snapshot_dir / f"{name}{tmpl.TEMPLATE_SUFFIX}"
