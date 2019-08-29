#!/usr/bin/env python3

import sys
import os
from pathlib import Path
import os.path as osp
from enum import Enum, auto
import filecmp
import re
import logging
from logging import ERROR, INFO,DEBUG
from typing import List, TextIO

import click

# from cmpdisktree import exclusions
from exclusions import EXCLUDE_PATTERNS_DEFAULT

#
# Helper classes
#

class FileKind(Enum):
    """Type of file"""
    FILE = 'File'
    DIR = 'Directory'
    SYMLINK = 'Symlink'

class ErrorKind(Enum):
    """Different errors that can occur"""
    NOT_EXIST_IN_1 = 'PATH does not exist in DIR1' # In msg the word PATH might be replaced file kind
    NOT_EXIST_IN_2 = 'PATH does not exist in DIR2' # In msg the word PATH might be replaced file kind
    DIFF = 'Content is different'
    NOACCESS = 'No access to PATH (e.g. file permissions)' # In msg the word PATH might be replaced file kind

    def txt(self, fkind: FileKind):
        return str(self.value).replace('PATH', fkind.value)


LOG_BACKUP_EXT = '.bak'

class LogFile():
    """
    Write information to a log file

    Features:
    - File is ONLY created when first written to
    - Possible old file (from previous run) is ALWAYS move to *.bak
    """
    def __init__(self, fname):
        self.fname = fname
        self.fobject = None
        pf = Path(fname)
        if pf.is_file():
            pf.rename(pf.with_name(pf.name+LOG_BACKUP_EXT))

    def close_if_needed(self):
        """Close file"""
        if self.fobject:
            return self.fobject.close()


    def write(self, str):
        if not self.fobject:
            self.fobject =  open(self.fname, 'w')
        print(str, file=self.fobject)

ERR_LOG_DEFAULT_NAME = 'cmp-err.log'
OK_LOG_DEFAULT_NAME = 'cmp-ok.log'

#
# Main Class
#
class Compare():
    """Compare two filesystems"""

    # list of folders not to traverse
    exclude_patterns = EXCLUDE_PATTERNS_DEFAULT
    used_exclude_patterns = set([])

    everything_ok = True

    def __init__(self, dir1, dir2,
                 verbose=False,
                 quiet=False,
                 report_identical=False,
                 structure_only=False,
                 shallow_compare=False):
        self.dir1 = Path(dir1)
        self.dir2 = Path(dir2)

        self.verbosity = INFO
        if quiet: self.verbosity = ERROR
        if verbose: self.verbosity = DEBUG

        self.err_log = LogFile(ERR_LOG_DEFAULT_NAME)
        self.ok_log = LogFile(OK_LOG_DEFAULT_NAME)

        self.report_identical = report_identical
        self.shallow_compare = shallow_compare
        self.structure_only = structure_only
        # Initialisations
        filecmp.clear_cache()

    def path_text(self, path1: Path, path2: Path):
        """Output of paths - Normally only path1, except for DEBUG"""
        if self.verbosity <= DEBUG:
            return f"{path1} | {path2}"
        else:
            return f"{path1}"

    def error(self, err: ErrorKind, fkind: FileKind, path1: Path, path2: Path, message: str = ''):
        """Report errors"""
        self.everything_ok = False
        msg = f"Error: {err.txt(fkind)} ({self.path_text(path1, path2)})"
        self.echo(DEBUG, msg)
        self.err_log.write(msg)

    cnt = 0
    myl = []
    def ok(self, fkind: FileKind, path1: Path, path2: Path, message: str = ''):
        """
        Report entries which are ok
        This is normally muted"""
        if self.report_identical:
            self.myl.append(str(path1))
            msg = self.path_text(path1, path2)
            # self.echo(DEBUG, f"OK: {msg}")
            # self.ok_log.write(msg)
            if self.cnt % 10000 == 0:
                self.ok_log.write(str(path1))
                self.ok_log.write(f"len(myl) = {len(self.myl)} | size(myl) = {sys.getsizeof(self.myl) // 1000} KB")
            self.cnt += 1

    def echo(self, level, message, *args):
        if level >= self.verbosity:
            try:
                msg = str.format(message, *args)
            except Exception:
                msg = message
            if level <= DEBUG:
                msg = f"{logging.getLevelName(level)}: {msg}"
            click.echo(msg)


    def make_dir2_path(self, path):
        """
        Generate a path under dir2 from a path under dir1
        """
        rel = Path(path).relative_to(self.dir1)
        return self.dir2.joinpath(rel)

    def cmp_files(self, path1: Path, path2: Path):
        if self.structure_only:
            self.ok(FileKind.FILE, path1, path2)
        else:
            try:
                res = filecmp.cmp(path1, path2, shallow=self.shallow_compare)
                if res:
                    self.ok(FileKind.FILE, path1, path2)
                else:
                    self.error(ErrorKind.DIFF, FileKind.FILE, path1, path2)
            except PermissionError:
                self.error(ErrorKind.NOACCESS, FileKind.FILE, path1, path2)

    def cmp_list(self, list, ikind: FileKind, path1: Path, path2: Path):
        """
        Compare whether a file entry list from path1 exists in path2
        In the case of files attempt a content comparison.

        :param list: the file of either directories or files
        :param contains_dirs: True if list contains directories, otherwise False
        """

        for e in list:
            e_in_1 = path1.joinpath(e)
            e_in_2 = path2.joinpath(e)

            isit = osp.isdir if ikind is FileKind.DIR else osp.isfile
            if isit(e_in_2) and not e_in_2.is_symlink():
                self.ok(ikind, e_in_1, e_in_2)
            else:
                self.error(ErrorKind.NOT_EXIST_IN_2, ikind, e_in_1, e_in_2)

    def excluded(self, path):
        """Check whether PATH is exclude through the exclude_patterns"""
        for pat in self.exclude_patterns:
            if re.fullmatch(pat, path):
                if not pat in self.used_exclude_patterns:
                    self.echo(DEBUG, "Pattern '{}' used (1st time for '{}')", pat, path)
                    self.used_exclude_patterns.add(pat)
                return True
        return False

    def work(self):
        try:
            for dirpath, subdirs, filenames in os.walk(self.dir1):

                if not self.excluded(dirpath):
                    dirpath = Path(dirpath)
                    dir2path = self.make_dir2_path(dirpath)
                    if dir2path.exists() and dir2path.is_dir():
                        self.cmp_list(subdirs, FileKind.DIR, dirpath, dir2path)
                        self.cmp_list(filenames, FileKind.FILE, dirpath, dir2path)
                    else:
                        self.error(ErrorKind.NOT_EXIST_IN_2, FileKind.DIR, dirpath, dir2path)
        finally:
            self.err_log.close_if_needed()
            self.ok_log.close_if_needed()

        if self.everything_ok:
            self.echo(INFO, "Compare ok.")
            exitcode = 0
        else:
            self.echo(INFO, f"Compare error(s) - First 5 lines below (for more see file '{self.err_log.fname}'):")
            with open(self.err_log.fname, 'r') as f:
                for  i,l in enumerate(f):
                    if i>4: break
                    click.echo(l,nl=False)
            exitcode = 1
        return exitcode


class ExpandedPath(click.Path):
    def convert(self, value, *args, **kwargs):
        value = os.path.expanduser(value)
        return super(ExpandedPath, self).convert(value, *args, **kwargs)

@click.command(help=f"""Compare the directories DIR1 and DIR2 as macOS disk structures

Errors are reported to a file (default '{ERR_LOG_DEFAULT_NAME}')
""")
@click.argument('dir1', type=ExpandedPath(exists=True))
@click.argument('dir2', type=ExpandedPath(exists=True))
@click.option('-v','--verbose', is_flag=True,
              help="Print debug output.")
@click.option('-q','--quiet', is_flag=True,
              help="No informational output.")
@click.option('-i', '--report-identical', is_flag=True,
              help=f"Report identical files to file (default: '{OK_LOG_DEFAULT_NAME}')")
@click.option('-s', '--structure-only', is_flag=True,
              help="Don't compare file content")
def main(*args, **kwargs):
    """Compare the directories DIR1 and DIR2 as macOS disk structures
    """
    cc = Compare(**kwargs)
    status = cc.work()
    sys.exit(status)

if __name__ == '__main__':
    main()
