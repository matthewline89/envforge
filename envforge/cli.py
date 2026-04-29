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
