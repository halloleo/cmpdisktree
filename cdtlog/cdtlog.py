"""
cdtlog - cmpdisktree log analytics
"""
from typing import List

import os
import sys
import collections
from pathlib import Path
import click

from cdtlog.common import ErrorKind, FileKind, ERR_LOG_DEFAULT_NAME



class Analytics():
    def __init__(self, logfile, details):
        self.read_errs = []
        self.errs = []
        self.pathinfos = []
        self.comments = []

        self.err_freq = collections.Counter()
        self.comment_freq = collections.Counter()
        self.pathdirs_freq = collections.Counter() # Freq of parent attributes
        self.pnames_freq = collections.Counter()
        self.pext_freq = collections.Counter()

        self.details = details
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

    #
    # The parsing and frequencing of the data
    #
    def load_data(self, logfile):
        """Load the data into the dicts"""
        for l in logfile:
            (err, pathinfo, comment) = self.parse_line(l.strip())
            self.errs.append(err)
            self.pathinfos.append(pathinfo)
            self.comments.append(comment)

        self.err_freq = collections.Counter(self.errs)
        self.comment_freq = collections.Counter(self.comments)
        for p in self.pathinfos:
            self.pnames_freq.update([Path(p).name])
            self.pathdirs_freq.update([Path(p).parent])
            self.pext_freq.update([Path(p).suffix])

    def print_h3(self, title):
        print()
        print(f"{title.upper()}:")
        print("-" * len(title))

    def print_freq(self, freqname: str, forced_val_parts=None, most_common=5):
        """Report values in freq"""
        def item_of_contains(l, v):
            return any([(v in itm) for itm in l])

        if forced_val_parts is None:
            forced_val_parts = []

        self.print_h3(freqname)
        freq = getattr(self, freqname)
        if not isinstance(freq, collections.Counter):
            raise ValueError(f"'{freqname}' is not a Counter type")

        i_old = 0
        more = False
        for (i, (val, num)) in enumerate(freq.most_common()):
            if item_of_contains(forced_val_parts, val) or (i < most_common):
                if i-i_old >1:
                    print ("...")
                i_old=i
                prval = f"'{val}'" if val != '' else "EMPTY"
                print(f"{prval} ({num})")
                more = False
            else:
                more = True
        if more:
            print("...")

    def report_errs_and_comments(self):
        self.print_freq('err_freq', [
            ErrorKind.NOT_EXIST_IN_1.txt(FileKind.FILE) # 'File does not exist in FS1'
            ],
            most_common=10)
        self.print_freq('comment_freq')

        self.print_freq('pathdirs_freq')
        if self.details:
            self.print_freq('pnames_freq')
            self.print_freq('pext_freq')


@click.command(
    help=f"""
Analyse the logs from cmpdisktree

Default log file is '{ERR_LOG_DEFAULT_NAME}'
""")
@click.argument('logfile', type=click.File('r'), nargs=1)
@click.option('-d', '--details', is_flag=True,
              help="Output details which are ususally not relevant. (file extension and"
                   " file stem frequencies)")
def main(logfile, details):
    """
    Analyse the logs from cmpdisktree
    """
    a = Analytics(logfile, details)
    a.report_errs_and_comments()

    print()


def contained_in_item_of(v, l):
    return any([(v in itm) for itm in l])
