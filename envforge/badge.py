"""Badge generation for snapshots — produce status badges (e.g. SVG/text) summarising snapshot metadata."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from envforge.snapshot import load
from envforge.lock import is_locked
from envforge.expire import is_expired
from envforge.lint import lint_snapshot


@dataclass
class BadgeInfo:
    snapshot: str
    var_count: int
    locked: bool
    expired: bool
    lint_errors: int
    lint_warnings: int

    @property
    def status(self) -> str:
        if self.expired:
            return "expired"
        if self.lint_errors:
            return "error"
        if self.locked:
            return "locked"
        if self.lint_warnings:
            return "warning"
        return "ok"


def collect_badge_info(snapshot_name: str, snapshot_dir: Path) -> BadgeInfo:
    """Gather metadata about a snapshot and return a BadgeInfo."""
    env = load(snapshot_name, snapshot_dir)
    locked = is_locked(snapshot_name, snapshot_dir)
    expired = is_expired(snapshot_name, snapshot_dir)
    report = lint_snapshot(snapshot_name, snapshot_dir)
    errors = sum(1 for i in report.issues if i.severity == "error")
    warnings = sum(1 for i in report.issues if i.severity == "warning")
    return BadgeInfo(
        snapshot=snapshot_name,
        var_count=len(env),
        locked=locked,
        expired=expired,
        lint_errors=errors,
        lint_warnings=warnings,
    )


_STATUS_COLOURS = {
    "ok": "#4c1",
    "locked": "#007ec6",
    "warning": "#dfb317",
    "error": "#e05d44",
    "expired": "#9f9f9f",
}


def render_svg(info: BadgeInfo) -> str:
    """Render a minimal flat SVG badge similar to shields.io style."""
    label = "envforge"
    message = f"{info.var_count} vars | {info.status}"
    colour = _STATUS_COLOURS.get(info.status, "#555")
    label_w = len(label) * 7 + 10
    msg_w = len(message) * 7 + 10
    total_w = label_w + msg_w
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="20">'
        f'<rect width="{label_w}" height="20" fill="#555"/>'
        f'<rect x="{label_w}" width="{msg_w}" height="20" fill="{colour}"/>'
        f'<text x="{label_w // 2}" y="14" fill="#fff" font-size="11" text-anchor="middle" font-family="DejaVu Sans">{label}</text>'
        f'<text x="{label_w + msg_w // 2}" y="14" fill="#fff" font-size="11" text-anchor="middle" font-family="DejaVu Sans">{message}</text>'
        "</svg>"
    )


def render_text(info: BadgeInfo) -> str:
    """Render a plain-text one-liner badge."""
    return f"[envforge] {info.snapshot} | {info.var_count} vars | {info.status}"


def save_badge(info: BadgeInfo, output: Path, fmt: str = "svg") -> Path:
    """Write badge to *output* file. fmt must be 'svg' or 'text'."""
    if fmt == "svg":
        content = render_svg(info)
        suffix = ".svg"
    elif fmt == "text":
        content = render_text(info)
        suffix = ".txt"
    else:
        raise ValueError(f"Unknown badge format: {fmt!r}")
    dest = output.with_suffix(suffix) if output.suffix == "" else output
    dest.write_text(content, encoding="utf-8")
    return dest
