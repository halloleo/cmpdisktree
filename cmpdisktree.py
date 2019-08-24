#!/usr/bin/env python3

import os
from pathlib import Path
from enum import Enum, auto
import filecmp
import re

import click


#
# Helpers
#
class ErrorKind(Enum):
    NOT_EXIST_IN_1 = 'Path does not exist in DIR1'
    NOT_EXIST_IN_2 = 'Path does not exist in DIR2'
    DIFF = 'Content is different'
    NOACCESS = 'No access (e.g. file permissions)'

class FileKind(Enum):
    FILE = 'File'
    DIR = 'Directory'
    SYMLINK = 'Symlink'
#
# Main Class
#
class Compare():

    # list of folders not to traverse
    exclude_patterns = ['/.DocumentRevisions-V100/.*',
                        '/.TemporaryItems/*']

    def __init__(self, dir1, dir2, report_identical=False, shallow_compare=False, structure_only=False):
        self.dir1 = Path(dir1)
        self.dir2 = Path(dir2)
        self.report_identical = report_identical
        self.shallow_compare = shallow_compare
        self.structure_only = structure_only
        # Initialisations
        filecmp.clear_cache()

    def error(self, errkind: ErrorKind, fkind: FileKind, path1: Path, path2: Path, message: str = ''):
        """Report errors"""
        print (f"Error \"{errkind.value} for {fkind.value}\": '{path1}' '{path2}'")

    def ok(self, fkind: FileKind, path1: Path, path2: Path, message: str = ''):
        """
        Report entries which are ok
        This is normally muted"""
        if self.report_identical:
            print (f"Identical {fkind.value}: '{path1}' '{path2}'")

    def info(self, message: str = ''):
        #print(message)
        pass


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
            if ikind is FileKind.DIR and e_in_2.is_dir() and not e_in_2.is_symlink():
                self.ok(FileKind.DIR, e_in_1, e_in_2)
            elif ikind is FileKind.FILE and e_in_2.is_file() and not e_in_2.is_symlink():
                self.cmp_files(e_in_1, e_in_2)

    def excluded(self, path):
        """Check whether PATH is exclude through the exclude_patterns"""
        for pat in self.exclude_patterns:
            if re.fullmatch(pat, path):
                self.info(f"'{path}' excluded because of pattern {pat}")
                return True
        return False

    def work(self):
        for dirpath, subdirs, filenames in os.walk(self.dir1):
            if not self.excluded(dirpath):
                dirpath = Path(dirpath)
                dir2path = self.make_dir2_path(dirpath)
                if dir2path.exists() and dir2path.is_dir():
                    self.cmp_list(subdirs, FileKind.DIR, dirpath, dir2path)
                    self.cmp_list(filenames, FileKind.FILE, dirpath, dir2path)
                else:
                    self.error(ErrorKind.NOT_EXIST_IN_2, FileKind.DIR, dirpath, dir2path)



class ExpandedPath(click.Path):
    def convert(self, value, *args, **kwargs):
        value = os.path.expanduser(value)
        return super(ExpandedPath, self).convert(value, *args, **kwargs)

@click.command()
@click.argument('dir1', type=ExpandedPath(exists=True))
@click.argument('dir2', type=ExpandedPath(exists=True))
@click.option('-s', '--report-identical', is_flag=True,
              help="Report identical files (might result in huge output)")
@click.option('-t', '--structure-only', is_flag=True,
              help="Don't compare file content")

def main(*args, **kwargs):
    """Compare the directories DIR1 and DIR2 as macOS disk structures"""
    cc = Compare(**kwargs)
    cc.work()


if __name__ == '__main__':
    main()
