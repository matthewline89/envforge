"""Root CLI entry-point for envforge."""
from __future__ import annotations

import click

from envforge.cli_snapshot import snapshot_group
from envforge.cli_diff import diff_group
from envforge.cli_restore import restore_group
from envforge.cli_merge import merge_group
from envforge.cli_tag import tag_group
from envforge.cli_search import search_group
from envforge.cli_template import template_group
from envforge.cli_compare import compare_group
from envforge.cli_encrypt import encrypt_group
from envforge.cli_alias import alias_group
from envforge.cli_watch import watch_group
from envforge.cli_pin import pin_group
from envforge.cli_export import export_group
from envforge.cli_audit import audit_group
from envforge.cli_validate import validate_group
from envforge.cli_rename import rename_group
from envforge.cli_clone import clone_group
from envforge.cli_snapshot_filter import filter_group
from envforge.cli_snapshot_score import score_group
from envforge.cli_snapshot_mirror import mirror_group
from envforge.cli_snapshot_digest import digest_group
from envforge.cli_snapshot_report import report_group
from envforge.cli_snapshot_meta import meta_group
from envforge.cli_snapshot_patch import patch_group
from envforge.cli_freeze import freeze_group
from envforge.cli_snapshot_trend import trend_group
from envforge.cli_quota import quota_group
from envforge.cli_snapshot_rating import rating_group
from envforge.cli_snapshot_health import health_group
from envforge.cli_snapshot_workflow import workflow_group
from envforge.cli_snapshot_verify import verify_group
from envforge.cli_snapshot_blame import blame_group
from envforge.cli_snapshot_activity import activity_group
from envforge.cli_snapshot_spotlight import spotlight_group
from envforge.cli_snapshot_category import category_group
from envforge.cli_snapshot_diff_history import diff_history_group
from envforge.cli_snapshot_bookmark_group import bookmark_group_group
from envforge.cli_snapshot_subscription import subscription_group
from envforge.cli_snapshot_dependency import dependency_group
from envforge.cli_snapshot_event import event_group
from envforge.cli_snapshot_chain import chain_group
from envforge.cli_slot import slot_group
from envforge.cli_snapshot_sort import sort_group
from envforge.cli_snapshot_preview import preview_group
from envforge.cli_schedule import schedule_group
from envforge.cli_archive import archive_group
from envforge.cli_lock import lock_group
from envforge.cli_annotate import annotate_group
from envforge.cli_namespace import namespace_group
from envforge.cli_group import group_group
from envforge.cli_bookmark import bookmark_group
from envforge.cli_pipeline import pipeline_group
from envforge.cli_trigger import trigger_group
from envforge.cli_label import label_group
from envforge.cli_replay import replay_group
from envforge.cli_snapshot_set import set_group
from envforge.cli_snapshot_streak import streak_group


@click.group()
@click.version_option()
def cli() -> None:
    """envforge — snapshot, diff, and restore environment variable sets."""


cli.add_command(snapshot_group, "snapshot")
cli.add_command(diff_group, "diff")
cli.add_command(restore_group, "restore")
cli.add_command(merge_group, "merge")
cli.add_command(tag_group, "tag")
cli.add_command(search_group, "search")
cli.add_command(template_group, "template")
cli.add_command(compare_group, "compare")
cli.add_command(encrypt_group, "encrypt")
cli.add_command(alias_group, "alias")
cli.add_command(watch_group, "watch")
cli.add_command(pin_group, "pin")
cli.add_command(export_group, "export")
cli.add_command(audit_group, "audit")
cli.add_command(validate_group, "validate")
cli.add_command(rename_group, "rename")
cli.add_command(clone_group, "clone")
cli.add_command(filter_group, "filter")
cli.add_command(score_group, "score")
cli.add_command(mirror_group, "mirror")
cli.add_command(digest_group, "digest")
cli.add_command(report_group, "report")
cli.add_command(meta_group, "meta")
cli.add_command(patch_group, "patch")
cli.add_command(freeze_group, "freeze")
cli.add_command(trend_group, "trend")
cli.add_command(quota_group, "quota")
cli.add_command(rating_group, "rating")
cli.add_command(health_group, "health")
cli.add_command(workflow_group, "workflow")
cli.add_command(verify_group, "verify")
cli.add_command(blame_group, "blame")
cli.add_command(activity_group, "activity")
cli.add_command(spotlight_group, "spotlight")
cli.add_command(category_group, "category")
cli.add_command(diff_history_group, "diff-history")
cli.add_command(bookmark_group_group, "bookmark-group")
cli.add_command(subscription_group, "subscription")
cli.add_command(dependency_group, "dependency")
cli.add_command(event_group, "event")
cli.add_command(chain_group, "chain")
cli.add_command(slot_group, "slot")
cli.add_command(sort_group, "sort")
cli.add_command(preview_group, "preview")
cli.add_command(schedule_group, "schedule")
cli.add_command(archive_group, "archive")
cli.add_command(lock_group, "lock")
cli.add_command(annotate_group, "annotate")
cli.add_command(namespace_group, "namespace")
cli.add_command(group_group, "group")
cli.add_command(bookmark_group, "bookmark")
cli.add_command(pipeline_group, "pipeline")
cli.add_command(trigger_group, "trigger")
cli.add_command(label_group, "label")
cli.add_command(replay_group, "replay")
cli.add_command(set_group, "set")
cli.add_command(streak_group, "streak")
