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
from envforge.cli_archive import archive_group
from envforge.cli_lock import lock_group
from envforge.cli_annotate import annotate_group
from envforge.cli_namespace import namespace_group
from envforge.cli_group import group_group
from envforge.cli_bookmark import bookmark_group
from envforge.cli_pipeline import pipeline_group
from envforge.cli_snapshot_filter import filter_group
from envforge.cli_snapshot_chain import chain_group
from envforge.cli_slot import slot_group
from envforge.cli_replay import replay_group
from envforge.cli_schedule import schedule_group
from envforge.cli_snapshot_score import score_group


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
cli.add_command(archive_group, "archive")
cli.add_command(lock_group, "lock")
cli.add_command(annotate_group, "annotate")
cli.add_command(namespace_group, "namespace")
cli.add_command(group_group, "group")
cli.add_command(bookmark_group, "bookmark")
cli.add_command(pipeline_group, "pipeline")
cli.add_command(filter_group, "filter")
cli.add_command(chain_group, "chain")
cli.add_command(slot_group, "slot")
cli.add_command(replay_group, "replay")
cli.add_command(schedule_group, "schedule")
cli.add_command(score_group, "score")
