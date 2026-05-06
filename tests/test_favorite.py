"""Tests for envforge.favorite."""
import pytest
from pathlib import Path
from envforge.favorite import (
    add_favorite,
    remove_favorite,
    list_favorites,
    is_favorite,
    _favorites_path,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def test_add_favorite_creates_favorites_file(snapshot_dir):
    add_favorite(snapshot_dir, "prod")
    assert _favorites_path(snapshot_dir).exists()


def test_add_favorite_stores_name(snapshot_dir):
    add_favorite(snapshot_dir, "prod")
    assert "prod" in list_favorites(snapshot_dir)


def test_add_favorite_returns_true_when_new(snapshot_dir):
    result = add_favorite(snapshot_dir, "staging")
    assert result is True


def test_add_favorite_returns_false_when_already_starred(snapshot_dir):
    add_favorite(snapshot_dir, "staging")
    result = add_favorite(snapshot_dir, "staging")
    assert result is False


def test_add_favorite_does_not_duplicate(snapshot_dir):
    add_favorite(snapshot_dir, "dev")
    add_favorite(snapshot_dir, "dev")
    assert list_favorites(snapshot_dir).count("dev") == 1


def test_remove_favorite_returns_true_when_found(snapshot_dir):
    add_favorite(snapshot_dir, "prod")
    result = remove_favorite(snapshot_dir, "prod")
    assert result is True


def test_remove_favorite_returns_false_when_missing(snapshot_dir):
    result = remove_favorite(snapshot_dir, "ghost")
    assert result is False


def test_remove_favorite_deletes_name(snapshot_dir):
    add_favorite(snapshot_dir, "prod")
    remove_favorite(snapshot_dir, "prod")
    assert "prod" not in list_favorites(snapshot_dir)


def test_list_favorites_returns_empty_when_none(snapshot_dir):
    assert list_favorites(snapshot_dir) == []


def test_list_favorites_returns_all_starred(snapshot_dir):
    add_favorite(snapshot_dir, "a")
    add_favorite(snapshot_dir, "b")
    favorites = list_favorites(snapshot_dir)
    assert "a" in favorites
    assert "b" in favorites


def test_is_favorite_true_when_starred(snapshot_dir):
    add_favorite(snapshot_dir, "prod")
    assert is_favorite(snapshot_dir, "prod") is True


def test_is_favorite_false_when_not_starred(snapshot_dir):
    assert is_favorite(snapshot_dir, "unknown") is False


def test_is_favorite_false_after_removal(snapshot_dir):
    add_favorite(snapshot_dir, "temp")
    remove_favorite(snapshot_dir, "temp")
    assert is_favorite(snapshot_dir, "temp") is False
