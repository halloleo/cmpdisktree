"""
cdtlog - cmpdisktree log analytics
"""
from typing import List

import os
import sys
import collections

import click

from cdtlog import common


class Analytics():
    def __init__(self, logfile):
        self.read_errs = []

        self.errs = []
        self.pathinfos = []
        self.comments = []

        self.err_freq = collections.Counter()
        self.pathinfo_freq = collections.Counter()
        self.comment_freq = collections.Counter()
        self.load_data(logfile)

    def add_error(self, comment, line: str) -> None:
        self.read_errs.append((comment, line))

    def parse_line(self, l: str) -> List:
        parts = l.split(' | ')
        if len(parts) < 2:
            self.add_error("No ' | ' dividers", l)
            return

        if len(parts) > 2:
            self.add_error("Too many ' | ' dividers", l)

        err = parts[0]
        leftover = parts[1]

        parts = leftover.split(' || COMMENT: ')

        if len(parts) > 2:
            self.add_error("Too many ' || ' dividers", l)

        path = parts[0]
        comment = parts[1] if len(parts) > 1 else ""

        return (err, path, comment)

    def load_data(self, logfile):
        """Load the data into the dicts"""
        for l in logfile:
            (err, pathinfo, comment) = self.parse_line(l.strip())
            self.errs.append(err); self.pathinfos.append(pathinfo); self.comments.append(comment)
        self.err_freq = collections.Counter(self.errs)
        self.pathinfo_freq = collections.Counter(self.pathinfos)
        self.comment_freq = collections.Counter(self.comments)

    def print_h3(self, title):
        print()
        print(f"{title.upper()}:")
        print("-" * len(title))

    def report_errs_and_comments(self):
        def print_freq(freqname, most_common=3):
            self.print_h3(freqname)
            freq = getattr(self, freqname)
            for (val, num) in freq.most_common(most_common):
                prval = f"'{val}'" if val != '' else "EMPTY"
                print(f"{prval} ({num})")
        print_freq('err_freq')
        print_freq('comment_freq')


@click.command(
    help=f"""
Analyse the logs from cmpdisktree

Default log file is '{common.ERR_LOG_DEFAULT_NAME}'
""")
@click.argument('logfile', type=click.File('r'), nargs=1)
def main(logfile):
    """
    Analyse the logs from cmpdisktree
    """
    a = Analytics(logfile)
    a.report_errs_and_comments()


if __name__ == '__main__':
    main()
