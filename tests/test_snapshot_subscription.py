"""Tests for envforge.snapshot_subscription."""
from __future__ import annotations

import pytest
from pathlib import Path

from envforge.snapshot_subscription import (
    SubscriptionEntry,
    SubscriptionReport,
    get_subscriptions,
    notify,
    subscribe,
    unsubscribe,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_subscribe_creates_subscriptions_file(snapshot_dir):
    subscribe(snapshot_dir, "alpha")
    assert (snapshot_dir / "subscriptions.json").exists()


def test_subscribe_returns_true_when_new(snapshot_dir):
    assert subscribe(snapshot_dir, "alpha") is True


def test_subscribe_returns_false_when_updated(snapshot_dir):
    subscribe(snapshot_dir, "alpha")
    assert subscribe(snapshot_dir, "alpha") is False


def test_subscribe_stores_event(snapshot_dir):
    subscribe(snapshot_dir, "alpha", event="save")
    report = get_subscriptions(snapshot_dir)
    assert report.entries[0].event == "save"


def test_subscribe_stores_label(snapshot_dir):
    subscribe(snapshot_dir, "alpha", label="my-label")
    report = get_subscriptions(snapshot_dir)
    assert report.entries[0].label == "my-label"


def test_unsubscribe_returns_true_when_found(snapshot_dir):
    subscribe(snapshot_dir, "alpha")
    assert unsubscribe(snapshot_dir, "alpha") is True


def test_unsubscribe_returns_false_when_not_found(snapshot_dir):
    assert unsubscribe(snapshot_dir, "ghost") is False


def test_unsubscribe_removes_entry(snapshot_dir):
    subscribe(snapshot_dir, "alpha")
    unsubscribe(snapshot_dir, "alpha")
    report = get_subscriptions(snapshot_dir)
    assert report.is_empty()


def test_get_subscriptions_returns_report(snapshot_dir):
    subscribe(snapshot_dir, "alpha")
    report = get_subscriptions(snapshot_dir)
    assert isinstance(report, SubscriptionReport)


def test_report_is_empty_when_no_subscriptions(snapshot_dir):
    report = get_subscriptions(snapshot_dir)
    assert report.is_empty()


def test_for_event_filters_correctly(snapshot_dir):
    subscribe(snapshot_dir, "alpha", event="save")
    subscribe(snapshot_dir, "beta", event="delete")
    report = get_subscriptions(snapshot_dir)
    assert len(report.for_event("save")) == 1
    assert report.for_event("save")[0].name == "alpha"


def test_for_event_includes_any(snapshot_dir):
    subscribe(snapshot_dir, "alpha", event="any")
    subscribe(snapshot_dir, "beta", event="save")
    report = get_subscriptions(snapshot_dir)
    assert len(report.for_event("save")) == 2


def test_notify_calls_matching_callbacks(snapshot_dir):
    subscribe(snapshot_dir, "alpha", event="save")
    called: list = []
    notify(snapshot_dir, "save", {"alpha": lambda e: called.append(e.name)})
    assert called == ["alpha"]


def test_notify_skips_missing_callbacks(snapshot_dir):
    subscribe(snapshot_dir, "alpha", event="save")
    notified = notify(snapshot_dir, "save", {})
    assert notified == []


def test_notify_returns_notified_names(snapshot_dir):
    subscribe(snapshot_dir, "alpha", event="any")
    notified = notify(snapshot_dir, "delete", {"alpha": lambda e: None})
    assert "alpha" in notified
