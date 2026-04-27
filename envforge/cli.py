"""Root CLI entry-point that registers all command groups."""

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


@click.group()
@click.version_option(package_name="envforge")
def cli() -> None:
    """envforge — snapshot, diff, and restore environment variable sets."""


cli.add_command(snapshot_group, name="snapshot")
cli.add_command(diff_group, name="diff")
cli.add_command(restore_group, name="restore")
cli.add_command(merge_group, name="merge")
cli.add_command(tag_group, name="tag")
cli.add_command(search_group, name="search")
cli.add_command(template_group, name="template")
cli.add_command(compare_group, name="compare")
cli.add_command(encrypt_group, name="encrypt")


if __name__ == "__main__":  # pragma: no cover
    cli()
