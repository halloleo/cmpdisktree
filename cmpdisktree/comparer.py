#!/usr/bin/env python3

import errno
import filecmp
import fnmatch
import logging
import os
import pprint as pp
import sys
from logging import DEBUG, ERROR, INFO
from pathlib import Path

import click

from cmpdisktree import debug, exclusions, utils
from cmpdisktree.utils import Display, ErrorKind, FileKind, OpMode


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
        traversal_only=False,
        shallow_compare=False,
        clear_std_exclusions=False,
        live_fs_exclusions=False,
        ignore_missing_in_fs1=False,
        relative_fs_top=False,
        output_path=None,
        # hidden options - not in help or doco:
        force_progress=None,
    ):
        """

        :param fs1: Top of filesystem 1
        :param fs2: Top of filesystem 2
        :param verbose: Verbose output
        :param quiet: Report only errors (no progress bar)
        :param report_identical: Create cmp-ok.log
        :param traversal_only: Do only phase 1 (traversal)
        :param shallow_compare: Passed to filecmp
        :param clear_std_exclusions: No exclusions
        :param live_fs_exclusions:Add exclusions for live FS
        :param relative_fs_top: Top doesn't need tio be a macOS disk top
        :param output_path: Output path for report file
        :param force_progress: True: show for sure progress bar
                               False: show for sure NO progress bar
                               None: let tqdm handle it (depends on tty)
        """
        # Set parameters
        self.fs1 = Path(fs1)
        self.fs2 = Path(fs2)

        self.verbosity = INFO

        # Set disable_progress to True/False only if force_progress is actively set
        self.disable_progress = None if force_progress is None else not force_progress
        if quiet:
            self.verbosity = ERROR
            # Only overwrite disable_progress only if force_progress is not actively set
            if force_progress is None:
                self.disable_progress = True
        if verbose:
            self.verbosity = DEBUG

        self.display = None
        self.echo(DEBUG, "main params = \n{}".format(pp.pformat(locals())))

        self.report_identical = report_identical
        self.shallow_compare = shallow_compare
        self.traversal_only = traversal_only
        self.clear_std_exclusions = clear_std_exclusions
        self.live_fs_exclusions = live_fs_exclusions
        self.ignore_missing_in_fs1 = ignore_missing_in_fs1
        self.relative_fs_top = relative_fs_top
        self.output_path = output_path

        # Initialisations
        # List of folders not to traverse:
        if self.clear_std_exclusions:
            self.exclude_patterns = []
        else:
            self.exclude_patterns = exclusions.STANDARD_EXCLUDE_PATTERNS
            if self.live_fs_exclusions:
                self.exclude_patterns.extend(exclusions.ADD_LIVEFS_EXCLUDE_PATTERNS)

        self.echo(
            DEBUG, "exclude patterns= \n{}".format(pp.pformat(self.exclude_patterns))
        )

        # Keep track whether pattern was already used in a first match:
        self.used_exclude_patterns = set([])
        # Memorise paths of the files in DIR1 to be compared:
        self.files_to_compare = []
        # Keep track that ALL comparison are ok:
        self.everything_ok = True

        # The log files
        self.err_log = utils.LogFile(
            self.output_path, utils.ERR_LOG_DEFAULT_NAME, force_default=False
        )
        self.ok_log = utils.LogFile(
            self.output_path, utils.OK_LOG_DEFAULT_NAME, force_default=True
        )

        # Standard lib filecmp caches file stats.
        filecmp.clear_cache()

    def in_debug_mode(self):
        """Are in debug mode?"""
        return self.verbosity <= DEBUG

    def add_comment(self, text: str):
        if text is None or text == '':
            return ''
        else:
            return ' || COMMENT: ' + text

    def make_rel_from_where_ever(self, path):
        """Make path relative. Try FS1 then FS2"""
        try:
            rel = Path(path).relative_to(self.fs1)
        except ValueError:
            try:
                rel = Path(path).relative_to(self.fs2)
            except ValueError:
                rel = path
        return rel

    def path_err_text(self, path: Path):
        """Output of paths - Normally only path1, except for DEBUG"""
        if self.in_debug_mode():
            rel_path = '/' + str(self.make_rel_from_where_ever(path))
            return f"{path} || REL: {rel_path}"
        else:
            return f"{path}"

    def error(self, err: ErrorKind, fkind: FileKind, path: Path, *, comment: str = ''):
        """Report errors"""
        self.everything_ok = False
        msg = (
            f"Error: {err.txt(fkind)} | {self.path_err_text(path)}"
            + self.add_comment(comment)
        )
        self.err_log.write(msg)

    def path_ok_text(self, path1, path2: Path):
        """Output of paths - Normally only path1, except for DEBUG"""
        if self.in_debug_mode():
            return f"{path1} || {path2}"
        else:
            return f"{path1}"

    def ok(self, fkind: FileKind, path: Path, comment: str = ''):
        """
        Report entries which are ok
        This is normally muted"""
        if self.report_identical:
            msg = self.path_err_text(path) + self.add_comment(comment)
            self.ok_log.write(msg)

    def echo(self, level, message, *args):
        """
        Informational echo output

        Is handled by Display class if instantiated
        """
        if level >= self.verbosity:
            try:
                msg = str.format(message, *args)
            except Exception:
                msg = message

            if self.in_debug_mode() and level != INFO:
                msg = f"{logging.getLevelName(level)}: {msg}"

            try:
                self.display.echo(msg)
            except AttributeError:
                click.echo(msg)

    def make_fs2_path(self, path):
        """
        Generate a path under dir2 from a path under dir1
        """
        rel = Path(path).relative_to(self.fs1)
        return self.fs2.joinpath(rel)

    def add_to_compare(self, path1: Path):
        """Add to the files_to_compare list"""
        if not self.traversal_only:
            self.files_to_compare.append(path1)

    def cmp_list_symlink_entry(self, ekind, e_in_1, e_in_2):
        """
        Compare list entry which is a symlink
        """
        lnk_in_1 = os.readlink(e_in_1)

        try:
            lnk_in_2 = os.readlink(e_in_2)
            if lnk_in_1 == lnk_in_2:
                self.ok(ErrorKind.DIFF, FileKind.SYMLINK, e_in_1)
            else:
                self.error(ErrorKind.DIFF, FileKind.SYMLINK, e_in_1)
        except OSError:
            # entry still might exists (just not a symlink!
            if e_in_2.exists():
                self.error(ErrorKind.MISMATCH, FileKind.SYMLINK, e_in_1)
            else:
                self.error(ErrorKind.NOT_EXIST_IN_2, ekind, e_in_1)

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
                # Do bot record DIR as identical (because their files might differ)
                # self.ok(ikind, e_in_1)

                # Keep this entry (a dir) for traversal!
                keep = True
        else:
            # e_in_2 is a symlink
            self.error(
                ErrorKind.MISMATCH, ikind, e_in_2, comment="FS2 entry is symlink"
            )
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
            if not self.excluded(e_in_1,self.fs1):
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
                                self.error(ErrorKind.NOT_EXIST_IN_2, ikind, e_in_1)
                except PermissionError as err:
                    debug.dbg_long_exception(err)
                    # We get here if we have a permission error in e1
                    # So lets try the same to e2
                    try:
                        e_in_2.is_symlink()
                        # e2 is readable, so e1 is a **singular** NOACCESS error
                        self.error(
                            ErrorKind.NOACCESS,
                            ikind,
                            e_in_1,
                            comment="FS1 entry not accessible",
                        )

                    except PermissionError as err2:
                        debug.dbg_long_exception(err2)
                        self.error(
                            ErrorKind.NOACCESS, ikind, e_in_2, "FS2 entry not accessible"
                        )

            if e in reduce_list2:  # doesn't need to be in list2
                reduce_list2.remove(e)

            if not keep_on_master_list:
                # The following removes the element from in the
                # **passed-in** list so that os.walk doesn't go into it
                # (if it is a directory)
                master_list.remove(e)

            self.display.update()

        if len(reduce_list2) > 0:
            for extra in reduce_list2:
                e_in_2 = path2.joinpath(extra)
                if not self.excluded(e_in_2, self.fs2) and \
                   not self.ignore_missing_in_fs1:
                    self.error(ErrorKind.NOT_EXIST_IN_1, ikind, e_in_2)

    def excluded(self, path, ref_fs):
        """
        Check whether PATH is excluded through the exclude_patterns
        :param path: Path to check
        :param ref_fs: The filesystem (fs1 or fs2) which is the "top" of path
        :return: Whether path should be excluded
        """
        # path_from_top
        pathstr = '/' + str(Path(path).relative_to(ref_fs))

        for pat in self.exclude_patterns:
            front_only = False
            if pat.startswith('/'):
                pat = pat[1:]
                if not self.relative_fs_top:
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

    def oswalk_error(self, e:OSError):
        ikind = FileKind.UNKOWN
        try:
            if Path(e.filename).is_dir():
                ikind = FileKind.DIR
        except:
            pass

        if e.errno == errno.EACCES:
            # Expected Permission Error
            details = f"{e} " if self.in_debug_mode() else ""
            comment = f"PermissionError {details}as user {utils.get_username()}"
        else:
            comment = f"UNEXPECTED {e}"
        self.error(ErrorKind.NOACCESS, ikind, e.filename, comment=comment)

    def work_phase1_traverse(self):
        """Traverse the filesystems"""
        try:
            self.display = Display(mode=OpMode.TRAVERSE, disable=self.disable_progress)
            for dirpath, subdirs, filenames in os.walk(self.fs1, onerror=self.oswalk_error):
                # Not sure whether the following excluded() call is not/cannot be
                # covered by the excluded() call in cmp_list...
                if not self.excluded(dirpath, self.fs1):
                    dirpath = Path(dirpath)
                    dir2path = self.make_fs2_path(dirpath)
                    # Get the dirs and files under dir2path
                    walked_into_dir2path = False
                    for dirpath2_walk, subdirs2_walk, filenames2_walk in os.walk(
                        dir2path, onerror=self.oswalk_error
                    ):
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
                            self.error(ErrorKind.MISMATCH, FileKind.DIR, dirpath)
                    else:
                        self.error(ErrorKind.NOT_EXIST_IN_2, FileKind.DIR, dirpath)
        finally:
            self.display.close()

    def work_phase2_compare(self):
        """Compare the files in the files_to_compare list"""
        try:
            self.display = Display(
                total=len(self.files_to_compare),
                mode=OpMode.COMPARE,
                disable=self.disable_progress,
            )

            for path1 in self.files_to_compare:
                self.display.update()
                path2 = self.make_fs2_path(path1)
                try:
                    res = filecmp.cmp(path1, path2, shallow=self.shallow_compare)
                    if res:
                        self.ok(FileKind.FILE, path1)
                    else:
                        self.error(ErrorKind.DIFF, FileKind.FILE, path1)
                except PermissionError as e:
                    details = f"{e} " if self.in_debug_mode() else ""
                    comment = f"PermissionError {details}as user {utils.get_username()}"
                    self.error(ErrorKind.NOACCESS, FileKind.FILE, path1, comment=comment)
                except OSError as e:
                    comment = f"OSError {e} as user {utils.get_username()}"
                    self.error(ErrorKind.NOACCESS, FileKind.FILE, path1, comment=comment)

        finally:
            self.display.close()

    def error_report(self):
        """Print error report"""
        num_of_lines = 5
        with open(self.err_log.fpath, 'r') as f:
            report = []
            more = False

            for i, l in enumerate(f,1):
                if i >= num_of_lines:
                    more = True
                else:
                    report.append(l)

        if more:
            self.echo(
                INFO,
                f"Compare errors - First {num_of_lines} lines below "
                f"(for all {i} lines see file '{self.err_log.fpath}'):",
            )
        else:
            self.echo(
                INFO,
                f"Compare errors (find them as well "
                f"in file '{self.err_log.fpath}'):",
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
