"""Tests for envforge.import_ module."""

from __future__ import annotations

from pathlib import Path

import pytest

from envforge.import_ import (
    ImportError,
    import_dotenv,
    import_file,
    import_json,
    import_yaml,
)


# ---------------------------------------------------------------------------
# import_dotenv
# ---------------------------------------------------------------------------

def test_import_dotenv_basic_key_value():
    result = import_dotenv("FOO=bar\nBAZ=qux\n")
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_import_dotenv_strips_double_quotes():
    result = import_dotenv('KEY="hello world"')
    assert result["KEY"] == "hello world"


def test_import_dotenv_strips_single_quotes():
    result = import_dotenv("KEY='hello world'")
    assert result["KEY"] == "hello world"


def test_import_dotenv_ignores_comments():
    result = import_dotenv("# comment\nFOO=1")
    assert "# comment" not in result
    assert result["FOO"] == "1"


def test_import_dotenv_ignores_blank_lines():
    result = import_dotenv("\n\nFOO=1\n\n")
    assert result == {"FOO": "1"}


def test_import_dotenv_ignores_lines_without_equals():
    result = import_dotenv("NOEQUALS\nFOO=bar")
    assert "NOEQUALS" not in result
    assert result["FOO"] == "bar"


# ---------------------------------------------------------------------------
# import_json
# ---------------------------------------------------------------------------

def test_import_json_returns_dict():
    result = import_json('{"A": "1", "B": "2"}')
    assert result == {"A": "1", "B": "2"}


def test_import_json_coerces_values_to_str():
    result = import_json('{"PORT": 8080}')
    assert result["PORT"] == "8080"


def test_import_json_raises_on_invalid_json():
    with pytest.raises(ImportError, match="Invalid JSON"):
        import_json("not json")


def test_import_json_raises_on_non_object():
    with pytest.raises(ImportError, match="JSON root must be an object"):
        import_json('["a", "b"]')


# ---------------------------------------------------------------------------
# import_yaml
# ---------------------------------------------------------------------------

def test_import_yaml_returns_dict():
    result = import_yaml("FOO: bar\nBAZ: qux\n")
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_import_yaml_coerces_values_to_str():
    result = import_yaml("PORT: 9000")
    assert result["PORT"] == "9000"


def test_import_yaml_raises_on_non_mapping():
    with pytest.raises(ImportError, match="YAML root must be a mapping"):
        import_yaml("- item1\n- item2\n")


# ---------------------------------------------------------------------------
# import_file
# ---------------------------------------------------------------------------

def test_import_file_dotenv(tmp_path: Path):
    f = tmp_path / ".env"
    f.write_text("X=1\nY=2\n")
    assert import_file(f) == {"X": "1", "Y": "2"}


def test_import_file_json(tmp_path: Path):
    f = tmp_path / "env.json"
    f.write_text('{"A": "hello"}')
    assert import_file(f) == {"A": "hello"}


def test_import_file_yaml(tmp_path: Path):
    f = tmp_path / "env.yaml"
    f.write_text("FOO: bar\n")
    assert import_file(f) == {"FOO": "bar"}


def test_import_file_unsupported_extension(tmp_path: Path):
    f = tmp_path / "env.toml"
    f.write_text("")
    with pytest.raises(ImportError, match="Unsupported file extension"):
        import_file(f)
