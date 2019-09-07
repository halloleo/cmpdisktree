#!/usr/bin/env python3
"""
The CLI to cmpdisktree
"""

import os
import sys

import click

from cmpdisktree import comparer
from cmpdisktree import utils


class ExpandedPath(click.Path):
    def convert(self, value, *args, **kwargs):
        value = os.path.expanduser(value)
        return super(ExpandedPath, self).convert(value, *args, **kwargs)


@click.command(
    help=f"""Compare the directories FS1 and FS2 as macOS disk structures

Errors are reported to a file (default '{utils.ERR_LOG_DEFAULT_NAME}')
"""
)
@click.argument('fs1', type=ExpandedPath(exists=True))
@click.argument('fs2', type=ExpandedPath(exists=True))
@click.option('-v', '--verbose', is_flag=True, help="Print debug output.")
@click.option('-q', '--quiet', is_flag=True, help="No informational output.")
@click.option(
    '-i',
    '--report-identical',
    is_flag=True,
    help=f"Report identical files to file (default: '{utils.OK_LOG_DEFAULT_NAME}')",
)
@click.option('-s', '--structure-only', is_flag=True, help="Don't compare file content")
@click.option(
    '-c',
    '--clear-std-exclusions',
    is_flag=True,
    help="Don't use standard exclusions for macOS disk files systems",
)
@click.option(
    '-r',
    '--relative-fs-top',
    is_flag=True,
    help="Allow relative filesystem top (used when applying the exclusions)",
)
@click.option(
    '-o', '--output-path', type=ExpandedPath(), help="Output path for report file."
)
def main(*args, **kwargs):
    """
    Compare the directories FS1 and FS2 as macOS disk structures
    """
    cc = comparer.Comparer(**kwargs)
    status = cc.work()
    sys.exit(status)


if __name__ == '__main__':
    main()
