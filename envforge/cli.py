"""Main CLI entry-point for envforge."""
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
from envforge.cli_snapshot_preview import preview_group
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
from envforge.cli_snapshot_sort import sort_group
from envforge.cli_group import group_group
from envforge.cli_namespace import namespace_group
from envforge.cli_bookmark import bookmark_group
from envforge.cli_pipeline import pipeline_group
from envforge.cli_trigger import trigger_group
from envforge.cli_label import label_group
from envforge.cli_snapshot_set import set_group
from envforge.cli_replay import replay_group
from envforge.cli_snapshot_chain import chain_group
from envforge.cli_slot import slot_group
from envforge.cli_lock import lock_group
from envforge.cli_annotate import annotate_group
from envforge.cli_archive import archive_group
from envforge.cli_schedule import schedule_group
from envforge.cli_snapshot_diff_history import diff_history_group


@click.group()
@click.version_option()
def cli() -> None:
    """envforge — snapshot, diff, and restore environment variable sets."""


cli.add_command(snapshot_group)
cli.add_command(diff_group)
cli.add_command(restore_group)
cli.add_command(merge_group)
cli.add_command(tag_group)
cli.add_command(search_group)
cli.add_command(template_group)
cli.add_command(compare_group)
cli.add_command(encrypt_group)
cli.add_command(alias_group)
cli.add_command(watch_group)
cli.add_command(pin_group)
cli.add_command(export_group)
cli.add_command(audit_group)
cli.add_command(validate_group)
cli.add_command(rename_group)
cli.add_command(clone_group)
cli.add_command(filter_group)
cli.add_command(score_group)
cli.add_command(mirror_group)
cli.add_command(digest_group)
cli.add_command(report_group)
cli.add_command(meta_group)
cli.add_command(preview_group)
cli.add_command(patch_group)
cli.add_command(freeze_group)
cli.add_command(trend_group)
cli.add_command(quota_group)
cli.add_command(rating_group)
cli.add_command(health_group)
cli.add_command(workflow_group)
cli.add_command(verify_group)
cli.add_command(blame_group)
cli.add_command(activity_group)
cli.add_command(spotlight_group)
cli.add_command(category_group)
cli.add_command(sort_group)
cli.add_command(group_group)
cli.add_command(namespace_group)
cli.add_command(bookmark_group)
cli.add_command(pipeline_group)
cli.add_command(trigger_group)
cli.add_command(label_group)
cli.add_command(set_group)
cli.add_command(replay_group)
cli.add_command(chain_group)
cli.add_command(slot_group)
cli.add_command(lock_group)
cli.add_command(annotate_group)
cli.add_command(archive_group)
cli.add_command(schedule_group)
cli.add_command(diff_history_group)
