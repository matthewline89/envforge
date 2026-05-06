"""Tests for envforge.badge."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envforge.badge import (
    BadgeInfo,
    collect_badge_info,
    render_svg,
    render_text,
    save_badge,
)


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _write(snapshot_dir: Path, name: str, env: dict) -> None:
    (snapshot_dir / f"{name}.json").write_text(json.dumps(env), encoding="utf-8")


# ── BadgeInfo.status ──────────────────────────────────────────────────────────

def test_status_ok_when_clean():
    info = BadgeInfo("snap", 3, locked=False, expired=False, lint_errors=0, lint_warnings=0)
    assert info.status == "ok"


def test_status_expired_takes_priority():
    info = BadgeInfo("snap", 3, locked=True, expired=True, lint_errors=1, lint_warnings=2)
    assert info.status == "expired"


def test_status_error_when_lint_errors():
    info = BadgeInfo("snap", 3, locked=False, expired=False, lint_errors=2, lint_warnings=0)
    assert info.status == "error"


def test_status_locked():
    info = BadgeInfo("snap", 3, locked=True, expired=False, lint_errors=0, lint_warnings=0)
    assert info.status == "locked"


def test_status_warning_when_only_warnings():
    info = BadgeInfo("snap", 3, locked=False, expired=False, lint_errors=0, lint_warnings=1)
    assert info.status == "warning"


# ── render_text ───────────────────────────────────────────────────────────────

def test_render_text_contains_snapshot_name():
    info = BadgeInfo("mysnap", 5, False, False, 0, 0)
    assert "mysnap" in render_text(info)


def test_render_text_contains_var_count():
    info = BadgeInfo("mysnap", 5, False, False, 0, 0)
    assert "5 vars" in render_text(info)


def test_render_text_contains_status():
    info = BadgeInfo("mysnap", 5, False, False, 0, 0)
    assert "ok" in render_text(info)


# ── render_svg ────────────────────────────────────────────────────────────────

def test_render_svg_is_valid_xml():
    info = BadgeInfo("mysnap", 4, False, False, 0, 0)
    svg = render_svg(info)
    assert svg.startswith("<svg") and svg.endswith("</svg>")


def test_render_svg_contains_status_colour_for_ok():
    info = BadgeInfo("snap", 2, False, False, 0, 0)
    assert "#4c1" in render_svg(info)


def test_render_svg_contains_error_colour():
    info = BadgeInfo("snap", 2, False, False, lint_errors=1, lint_warnings=0)
    assert "#e05d44" in render_svg(info)


# ── save_badge ────────────────────────────────────────────────────────────────

def test_save_badge_svg_creates_file(tmp_path):
    info = BadgeInfo("snap", 3, False, False, 0, 0)
    dest = save_badge(info, tmp_path / "badge", fmt="svg")
    assert dest.exists()
    assert dest.suffix == ".svg"


def test_save_badge_text_creates_file(tmp_path):
    info = BadgeInfo("snap", 3, False, False, 0, 0)
    dest = save_badge(info, tmp_path / "badge", fmt="text")
    assert dest.exists()
    assert dest.suffix == ".txt"


def test_save_badge_raises_on_unknown_format(tmp_path):
    info = BadgeInfo("snap", 3, False, False, 0, 0)
    with pytest.raises(ValueError, match="Unknown badge format"):
        save_badge(info, tmp_path / "badge", fmt="png")


# ── collect_badge_info integration ───────────────────────────────────────────

def test_collect_badge_info_var_count(snapshot_dir):
    _write(snapshot_dir, "dev", {"A": "1", "B": "2"})
    info = collect_badge_info("dev", snapshot_dir)
    assert info.var_count == 2


def test_collect_badge_info_snapshot_name(snapshot_dir):
    _write(snapshot_dir, "dev", {"X": "y"})
    info = collect_badge_info("dev", snapshot_dir)
    assert info.snapshot == "dev"
