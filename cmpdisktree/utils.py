"""
General utility classes for cmpdisktree
"""
import os
import pwd
from enum import Enum, auto
from pathlib import Path
import time

from tqdm import tqdm
import click


def get_username():
    """Find username of invoking user"""
    return pwd.getpwuid( os.getuid()).pw_name

class FileKind(Enum):
    """Type of file"""

    FILE = 'File'
    DIR = 'Directory'
    SYMLINK = 'Symlink'


class ErrorKind(Enum):
    """
    The different errors that can occur

    Note: The txt() method generates a readable description - The word PATH
          might be replaced with the file kind or similar
    """

    NOT_EXIST_IN_1 = 'PATH does not exist in FS1'
    NOT_EXIST_IN_2 = (
        'PATH does not exist in FS2'
    )  # In txt() the word PATH might be replaced file kind
    DIFF = 'PATH is different'
    MISMATCH = 'Node type in FS2 is not PATH'
    NOACCESS = (
        'No access to PATH (e.g. file permissions)'
    )  # In txt() the word PATH might be replaced file kind

    def txt(self, fkind: FileKind):
        """Readable description of the error depending on the file kind"""
        if self is ErrorKind.DIFF and fkind is FileKind.FILE:
            return str(self.value).replace('PATH', 'Content')

        if self is ErrorKind.DIFF and fkind is FileKind.SYMLINK:
            return str(self.value).replace('PATH', 'Symlink target')

        return str(self.value).replace('PATH', fkind.value)


ERR_LOG_DEFAULT_NAME = 'cmp-err.log'
OK_LOG_DEFAULT_NAME = 'cmp-ok.log'
LOG_BACKUP_EXT = '.bak'


class LogFile:
    """
    Write information to a log file

    Features:
    - File is ONLY created when first written to
    - Possible old file (from previous run) is ALWAYS move to *.bak
    """

    def __init__(self, pathstr: str, default_name: str, force_default: bool):
        """

        :param pathstr: The path string from the command line or None
                        Can contain a free name part or
                        is just an existing directory
        :param default_name: The default name part of the path
        :param force_default: Use default_name as *name* part regardless
                              whether pathstr provides a name part.
        """
        if pathstr is None:
            pathstr = '.'
        path = Path(pathstr)
        if path.is_dir():
            self.fpath = path.joinpath(default_name)
        else:
            dirpath = path.parent
            if not dirpath.is_dir():
                raise click.BadParameter('Contains a non-existing directory',
                                         param_hint='output-path')
            if force_default:
                self.fpath = dirpath.joinpath(default_name)
            else:
                self.fpath = path

        self.fobject = None
        if self.fpath.is_file():
            self.fpath.rename(self.fpath.with_name(self.fpath.name + LOG_BACKUP_EXT))

    def close_if_needed(self):
        """Close file"""
        if self.fobject:
            self.fobject.close()
            self.fobject = None

    def write(self, txt: str):
        if not self.fobject:
            self.fobject = open(self.fpath, 'a')
        print(txt, file=self.fobject)
        self.close_if_needed()


class  Pbar(tqdm):
    BAR_FORMAT_BASE = '{l_bar}{bar}| {n_fmt}/{total_fmt} '
    BAR_FORMAT_TRAIL = ' '

    def __init__(self, iterable=None, **kwargs):
        defaults = {
            'ascii': True,
            'bar_format': self.BAR_FORMAT_BASE +
                          'Elap:{elapsed}s Remain:{remaining}s' +
                          self.BAR_FORMAT_TRAIL

        }
        for k in defaults:
            if not k in kwargs:
                kwargs[k] = defaults[k]

        return super(Pbar, self).__init__(iterable, **kwargs)

    def close(self):
        self.bar_format = self.BAR_FORMAT_BASE + \
                          'Total:{elapsed}s                   ' + \
                          self.BAR_FORMAT_TRAIL

        super(Pbar, self).close()
        if self.disable:
            return
        time.sleep(0.2)

