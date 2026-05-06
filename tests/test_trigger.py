"""Tests for envforge.trigger."""

from __future__ import annotations

from pathlib import Path

import pytest

from envforge.trigger import (
    TriggerEntry,
    TriggerResult,
    add_trigger,
    evaluate_trigger,
    list_triggers,
    remove_trigger,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_add_trigger_creates_triggers_file(snapshot_dir: Path) -> None:
    entry = TriggerEntry(name="t1", condition="key_added")
    add_trigger(snapshot_dir, entry)
    assert (snapshot_dir / "triggers.json").exists()


def test_add_trigger_returns_true_when_new(snapshot_dir: Path) -> None:
    entry = TriggerEntry(name="t1", condition="key_added")
    assert add_trigger(snapshot_dir, entry) is True


def test_add_trigger_returns_false_when_replaced(snapshot_dir: Path) -> None:
    entry = TriggerEntry(name="t1", condition="key_added")
    add_trigger(snapshot_dir, entry)
    updated = TriggerEntry(name="t1", condition="key_removed")
    assert add_trigger(snapshot_dir, updated) is False


def test_list_triggers_returns_entries(snapshot_dir: Path) -> None:
    add_trigger(snapshot_dir, TriggerEntry(name="a", condition="key_added"))
    add_trigger(snapshot_dir, TriggerEntry(name="b", condition="value_changed", target_key="FOO"))
    entries = list_triggers(snapshot_dir)
    assert len(entries) == 2
    names = {e.name for e in entries}
    assert names == {"a", "b"}


def test_list_triggers_empty_when_none(snapshot_dir: Path) -> None:
    assert list_triggers(snapshot_dir) == []


def test_remove_trigger_returns_true_when_found(snapshot_dir: Path) -> None:
    add_trigger(snapshot_dir, TriggerEntry(name="t1", condition="key_added"))
    assert remove_trigger(snapshot_dir, "t1") is True


def test_remove_trigger_returns_false_when_missing(snapshot_dir: Path) -> None:
    assert remove_trigger(snapshot_dir, "ghost") is False


def test_remove_trigger_decrements_list(snapshot_dir: Path) -> None:
    add_trigger(snapshot_dir, TriggerEntry(name="a", condition="key_added"))
    add_trigger(snapshot_dir, TriggerEntry(name="b", condition="key_removed"))
    remove_trigger(snapshot_dir, "a")
    assert len(list_triggers(snapshot_dir)) == 1


def test_evaluate_key_added_fires(snapshot_dir: Path) -> None:
    entry = TriggerEntry(name="t", condition="key_added", snapshot_prefix="trig")
    before = {"A": "1"}
    after = {"A": "1", "B": "2"}
    result = evaluate_trigger(snapshot_dir, entry, before, after, version="v1")
    assert result.triggered is True
    assert result.snapshot_name == "trig-t-v1"


def test_evaluate_key_added_no_fire_when_unchanged(snapshot_dir: Path) -> None:
    entry = TriggerEntry(name="t", condition="key_added")
    env = {"A": "1"}
    result = evaluate_trigger(snapshot_dir, entry, env, env.copy(), version="v1")
    assert result.triggered is False


def test_evaluate_key_removed_fires(snapshot_dir: Path) -> None:
    entry = TriggerEntry(name="t", condition="key_removed")
    before = {"A": "1", "B": "2"}
    after = {"A": "1"}
    result = evaluate_trigger(snapshot_dir, entry, before, after, version="v1")
    assert result.triggered is True


def test_evaluate_value_changed_fires(snapshot_dir: Path) -> None:
    entry = TriggerEntry(name="t", condition="value_changed", target_key="A")
    before = {"A": "old"}
    after = {"A": "new"}
    result = evaluate_trigger(snapshot_dir, entry, before, after, version="v1")
    assert result.triggered is True


def test_evaluate_value_changed_specific_key_no_fire(snapshot_dir: Path) -> None:
    entry = TriggerEntry(name="t", condition="value_changed", target_key="B")
    before = {"A": "old", "B": "same"}
    after = {"A": "new", "B": "same"}
    result = evaluate_trigger(snapshot_dir, entry, before, after, version="v1")
    assert result.triggered is False


def test_evaluate_creates_snapshot_file(snapshot_dir: Path) -> None:
    entry = TriggerEntry(name="t", condition="key_added", snapshot_prefix="snap")
    result = evaluate_trigger(snapshot_dir, entry, {}, {"X": "1"}, version="ts")
    assert result.triggered
    assert (snapshot_dir / f"{result.snapshot_name}.json").exists()
