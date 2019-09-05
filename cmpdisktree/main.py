#!/usr/bin/env python3

import filecmp
import fnmatch
import logging
import os
import pprint as pp
import sys
from logging import DEBUG, ERROR, INFO
from pathlib import Path

import click
from tqdm import tqdm

from cmpdisktree import debug
from cmpdisktree.exclusions import STANDARD_EXCLUDE_PATTERNS
from cmpdisktree.utils import ErrorKind, FileKind, LogFile

ERR_LOG_DEFAULT_NAME = 'cmp-err.log'
OK_LOG_DEFAULT_NAME = 'cmp-ok.log'


#
# Main Class
#
class Comparer:
    """Compare two filesystems"""

    def __init__(
        self,
        fs1,
        fs2,
        verbose=False,
        quiet=False,
        report_identical=False,
        structure_only=False,
        shallow_compare=False,
        clear_std_exclusions=False,
        relative_fs_top=False,
        output_path=None,
    ):
        # Set parameters
        self.fs1 = Path(fs1)
        self.fs2 = Path(fs2)

        self.verbosity = INFO
        if quiet:
            self.verbosity = ERROR
        if verbose:
            self.verbosity = DEBUG

        self.echo(DEBUG, "main params = \n{}".format(pp.pformat(locals())))

        self.report_identical = report_identical
        self.shallow_compare = shallow_compare
        self.structure_only = structure_only
        self.clear_std_exclusions = clear_std_exclusions
        self.relative_fs_top = relative_fs_top
        self.output_path = output_path

        # Initialisations
        # List of folders not to traverse:
        self.exclude_patterns = (
            [] if self.clear_std_exclusions else STANDARD_EXCLUDE_PATTERNS
        )
        # Keep track whether pattern was already used in a first match:
        self.used_exclude_patterns = set([])
        # Memorise paths of the files in DIR1 to be compared:
        self.files_to_compare = []
        # Keep track that ALL comparison are ok:
        self.everything_ok = True

        # The log files
        self.err_log = LogFile(ERR_LOG_DEFAULT_NAME)
        self.ok_log = LogFile(OK_LOG_DEFAULT_NAME)

        # Standard lib filecmp caches file stats.
        filecmp.clear_cache()

    def path_text(self, path1: Path, path2: Path):
        """Output of paths - Normally only path1, except for DEBUG"""
        if self.verbosity <= DEBUG:
            return f"{path1} || {path2}"
        else:
            return f"{path1}"

    def error(
        self,
        err: ErrorKind,
        fkind: FileKind,
        path1: Path,
        path2: Path,
        message: str = '',
    ):
        """Report errors"""
        self.everything_ok = False
        msg = f"Error: {err.txt(fkind)} | {self.path_text(path1, path2)})"
        self.echo(DEBUG, msg)
        self.err_log.write(msg)

    def ok(self, fkind: FileKind, path1: Path, path2: Path, message: str = ''):
        """
        Report entries which are ok
        This is normally muted"""
        if self.report_identical:
            msg = self.path_text(path1, path2)
            self.echo(DEBUG, f"OK: {msg}")
            self.ok_log.write(msg)

    def echo(self, level, message, *args):
        if level >= self.verbosity:
            try:
                msg = str.format(message, *args)
            except Exception:
                msg = message
            if level <= DEBUG:
                msg = f"{logging.getLevelName(level)}: {msg}"
            click.echo(msg)

    def make_fs2_path(self, path):
        """
        Generate a path under dir2 from a path under dir1
        """
        rel = Path(path).relative_to(self.fs1)
        return self.fs2.joinpath(rel)

    def add_to_compare(self, path1: Path):
        """Add to the files_to_compare list"""
        if not self.structure_only:
            self.files_to_compare.append(path1)

    def cmp_list_symlink_entry(self, ekind, e_in_1, e_in_2):
        """
        Compare list entry which is a symlink
        """
        lnk_in_1 = os.readlink(e_in_1)

        try:
            lnk_in_2 = os.readlink(e_in_2)
            if lnk_in_1 == lnk_in_2:
                self.ok(ErrorKind.DIFF, FileKind.SYMLINK, e_in_1, e_in_2)
            else:
                self.error(ErrorKind.DIFF, FileKind.SYMLINK, e_in_1, e_in_2)
        except OSError:
            # entry still might exists (just not a symlink!
            if e_in_2.exists():
                self.error(ErrorKind.MISMATCH, FileKind.SYMLINK, e_in_1, e_in_2)
            else:
                self.error(ErrorKind.NOT_EXIST_IN_2, ekind, e_in_1, e_in_2)

    def cmp_dir_or_file_entry(self, ikind, e_in_1, e_in_2):
        """
        Compare list entry which is a real directory or file

        :return: whether this entry should be kept for traversal
        """
        keep = False
        if not e_in_2.is_symlink():
            if ikind is FileKind.FILE:
                self.add_to_compare(e_in_1)
            else:
                # DIRs don't need to be compared
                self.ok(ikind, e_in_1, e_in_2)
                # Keep this entry (a dir) for traversal!
                keep = True
        else:
            # e_in_2 is a symlink
            self.error(ErrorKind.MISMATCH, ikind, e_in_1, e_in_2)
        return keep

    def cmp_list(self, master_list, list2, ikind: FileKind, path1: Path, path2: Path):
        """
        Compare whether a file entry list from path1 exists in path2
        In the case of files attempt a content comparison.

        :param master_list: the file of either directories or files
        :param ikind: the FileKind of the items in the list
                      (directories or files)

        Note: This function removes items from master_list when the comparision failed
        """

        loop_list = master_list.copy()
        reduce_list2 = list2.copy()
        for e in loop_list:
            e_in_1 = path1.joinpath(e)
            e_in_2 = path2.joinpath(e)

            # Tracks whether entry e can be traversed into
            keep_on_master_list = False

            try:
                if e_in_1.is_symlink():
                    # The "directory" or "file" might be a symlink:
                    self.cmp_list_symlink_entry(ikind, e_in_1, e_in_2)

                else:
                    # Real directory or file
                    if e in reduce_list2:  # this is equivalent to
                        # `if is_dir/is_file(e_in_2)`
                        if self.cmp_dir_or_file_entry(ikind, e_in_1, e_in_2):
                            # Keep this entry (a dir) for traversal!
                            keep_on_master_list = True
                    else:
                        if not self.excluded(e_in_2, self.fs2):
                            self.error(ErrorKind.NOT_EXIST_IN_2, ikind, e_in_1, e_in_2)
            except PermissionError as err:
                debug.dbg_long_exception(err)
                # We get here if we have a permission error in e1
                # So lets try the same to e2
                try:
                    e_in_2.is_symlink()
                    # e2 is readable, so e2 is a **singular** NOACCESS error
                    self.error(
                        ErrorKind.NOACCESS, ikind, 'SINGULAR | ' + str(e_in_1), '---'
                    )

                except PermissionError as err2:
                    debug.dbg_long_exception(err2)
                    self.error(
                        ErrorKind.NOACCESS, ikind, '---', 'SINGULAR | ' + str(e_in_2)
                    )

            if e in reduce_list2:  # doesn't need to be in list2
                reduce_list2.remove(e)

            if not keep_on_master_list:
                # The following removes the element from in the
                # **passed-in** list so that os.walk doesn't go into it
                # (if it is a directory)
                master_list.remove(e)

        if len(reduce_list2) > 0:
            for extra in reduce_list2:
                e_in_1 = path1.joinpath(extra)
                e_in_2 = path2.joinpath(extra)
                if not self.excluded(e_in_2, self.fs2):
                    self.error(ErrorKind.NOT_EXIST_IN_1, ikind, e_in_1, e_in_2)

    def excluded(self, path, ref_fs):
        """
        Check whether PATH is excluded through the exclude_patterns
        :param path: Path to check
        :param ref_fs: The filesystem (fs1 or fs2) which is the "top" of path
        :return: Whether path should be excluded
        """
        # path_from_top
        pathstr = '/'+str(Path(path).relative_to(ref_fs))

        for pat in self.exclude_patterns:
            front_only = False
            if pat.startswith('/'):
                pat = pat[1:]
                front_only = True

            if front_only:
                match_pat = '/' + pat
            else:
                match_pat = '*/' + pat

            if fnmatch.fnmatch(pathstr, match_pat):
                if not pat in self.used_exclude_patterns:
                    self.echo(
                        DEBUG, "Pattern '{}' used (1st time for '{}')", pat, pathstr
                    )
                    self.used_exclude_patterns.add(pat)
                return True
        return False

    def work_phase1_traverse(self):
        """Traverse the filesystems"""
        for dirpath, subdirs, filenames in os.walk(self.fs1):
            if not self.excluded(dirpath, self.fs1):
                dirpath = Path(dirpath)
                dir2path = self.make_fs2_path(dirpath)
                # Get the dirs and files under dir2path
                walked_into_dir2path = False
                for dirpath2_walk, subdirs2_walk, filenames2_walk in os.walk(dir2path):
                    walked_into_dir2path = True
                    subdirs2 = subdirs2_walk.copy()
                    filenames2 = filenames2_walk.copy()
                    subdirs2_walk.clear()
                if walked_into_dir2path:
                    if not dir2path.is_symlink():
                        self.cmp_list(
                            subdirs, subdirs2, FileKind.DIR, dirpath, dir2path
                        )
                        self.cmp_list(
                            filenames, filenames2, FileKind.FILE, dirpath, dir2path
                        )
                    else:
                        self.error(ErrorKind.MISMATCH, FileKind.DIR, dirpath, dir2path)
                else:
                    self.error(
                        ErrorKind.NOT_EXIST_IN_2, FileKind.DIR, dirpath, dir2path
                    )

    def work_phase2_compare(self):
        """Compare the files in the files_to_compare list"""
        for path1 in tqdm(self.files_to_compare):
            path2 = self.make_fs2_path(path1)
            try:
                res = filecmp.cmp(path1, path2, shallow=self.shallow_compare)
                if res:
                    self.ok(FileKind.FILE, path1, path2)
                else:
                    self.error(ErrorKind.DIFF, FileKind.FILE, path1, path2)
            except PermissionError:
                self.error(ErrorKind.NOACCESS, FileKind.FILE, path1, path2)

    def error_report(self):
        """Print error report"""
        num_of_lines = 5
        with open(self.err_log.fname, 'r') as f:
            report = []
            more = False
            for i, l in enumerate(f):
                if i >= num_of_lines:
                    more = True
                    break
                report.append(l)
        if more:
            self.echo(
                INFO,
                f"Compare errors - First {num_of_lines} lines below "
                f"(for more see file '{self.err_log.fname}'):",
            )
        else:
            self.echo(
                INFO,
                f"Compare errors (find them as well "
                f"in file '{self.err_log.fname}'):",
            )
        self.echo(INFO, "".join(report).strip())

    def work(self):
        try:
            self.work_phase1_traverse()
            # debug.dbg_print_ftc_list(self.files_to_compare)
            self.work_phase2_compare()
        finally:
            self.err_log.close_if_needed()
            self.ok_log.close_if_needed()

        # Result processing
        if self.everything_ok:
            self.echo(INFO, "Compare ok.")
            exitcode = 0
        else:
            self.error_report()
            exitcode = 1
        return exitcode


class ExpandedPath(click.Path):
    def convert(self, value, *args, **kwargs):
        value = os.path.expanduser(value)
        return super(ExpandedPath, self).convert(value, *args, **kwargs)


@click.command(
    help=f"""Compare the directories FS1 and FS2 as macOS disk structures

Errors are reported to a file (default '{ERR_LOG_DEFAULT_NAME}')
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
    help=f"Report identical files to file (default: '{OK_LOG_DEFAULT_NAME}')",
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
    cc = Comparer(**kwargs)
    status = cc.work()
    sys.exit(status)


if __name__ == '__main__':
    main()
