"""Tests for envforge.snapshot_rating."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.snapshot_rating import (
    RatingError,
    TopRated,
    get_rating,
    list_ratings,
    remove_rating,
    set_rating,
    top_rated,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_set_rating_creates_ratings_file(snapshot_dir: Path) -> None:
    set_rating(snapshot_dir, "snap1", 4)
    assert (snapshot_dir / "ratings.json").exists()


def test_set_rating_stores_value(snapshot_dir: Path) -> None:
    set_rating(snapshot_dir, "snap1", 3)
    data = json.loads((snapshot_dir / "ratings.json").read_text())
    assert data["snap1"] == 3


def test_set_rating_returns_true_when_new(snapshot_dir: Path) -> None:
    assert set_rating(snapshot_dir, "snap1", 5) is True


def test_set_rating_returns_false_when_updated(snapshot_dir: Path) -> None:
    set_rating(snapshot_dir, "snap1", 5)
    assert set_rating(snapshot_dir, "snap1", 2) is False


def test_set_rating_raises_for_zero(snapshot_dir: Path) -> None:
    with pytest.raises(RatingError):
        set_rating(snapshot_dir, "snap1", 0)


def test_set_rating_raises_for_six(snapshot_dir: Path) -> None:
    with pytest.raises(RatingError):
        set_rating(snapshot_dir, "snap1", 6)


def test_set_rating_accepts_boundary_values(snapshot_dir: Path) -> None:
    set_rating(snapshot_dir, "a", 1)
    set_rating(snapshot_dir, "b", 5)
    assert get_rating(snapshot_dir, "a") == 1
    assert get_rating(snapshot_dir, "b") == 5


def test_get_rating_returns_none_when_missing(snapshot_dir: Path) -> None:
    assert get_rating(snapshot_dir, "nope") is None


def test_get_rating_returns_stored_value(snapshot_dir: Path) -> None:
    set_rating(snapshot_dir, "snap1", 4)
    assert get_rating(snapshot_dir, "snap1") == 4


def test_remove_rating_returns_true_when_found(snapshot_dir: Path) -> None:
    set_rating(snapshot_dir, "snap1", 3)
    assert remove_rating(snapshot_dir, "snap1") is True


def test_remove_rating_returns_false_when_missing(snapshot_dir: Path) -> None:
    assert remove_rating(snapshot_dir, "ghost") is False


def test_remove_rating_deletes_entry(snapshot_dir: Path) -> None:
    set_rating(snapshot_dir, "snap1", 2)
    remove_rating(snapshot_dir, "snap1")
    assert get_rating(snapshot_dir, "snap1") is None


def test_list_ratings_returns_all(snapshot_dir: Path) -> None:
    set_rating(snapshot_dir, "a", 1)
    set_rating(snapshot_dir, "b", 5)
    result = list_ratings(snapshot_dir)
    assert result == {"a": 1, "b": 5}


def test_top_rated_returns_top_rated_entries(snapshot_dir: Path) -> None:
    set_rating(snapshot_dir, "a", 2)
    set_rating(snapshot_dir, "b", 5)
    set_rating(snapshot_dir, "c", 3)
    top = top_rated(snapshot_dir, limit=2)
    assert len(top) == 2
    assert top[0].name == "b"
    assert top[0].stars == 5


def test_top_rated_returns_empty_when_no_ratings(snapshot_dir: Path) -> None:
    assert top_rated(snapshot_dir) == []
