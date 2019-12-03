"""
General utility classes for cmpdisktree
"""
import os
import pwd
import subprocess
import time
from enum import Enum, auto
from pathlib import Path

import click
from tqdm import tqdm


def get_username():
    """Find username of invoking user"""
    return pwd.getpwuid(os.getuid()).pw_name


class FileKind(Enum):
    """Type of file"""

    FILE = 'File'
    DIR = 'Directory'
    SYMLINK = 'Symlink'
    UNKOWN = 'Unkown'


class ErrorKind(Enum):
    """
    The different errors that can occur

    Note: The txt() method generates a readable description - The word PATH
          might be replaced with the file kind or similar
    """

    # The word PATH in the followingen enum values is replaced by FileKind
    NOT_EXIST_IN_1 = 'PATH does not exist in FS1'
    NOT_EXIST_IN_2 = 'PATH does not exist in FS2'
    DIFF = 'PATH is different'
    MISMATCH = 'Node type in FS2 is not PATH'
    NOACCESS = 'No access to PATH'

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
                raise click.BadParameter(
                    'Contains a non-existing directory', param_hint='output-path'
                )
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


def get_terminal_size():
    """
    Determine terminal dimensions

    From tldr.py
    """
    def get_terminal_size_stty():
        try:
            return map(int, subprocess.check_output(['stty', 'size'],stderr=subprocess.STDOUT).split())
        except:
            pass

    def get_terminal_size_tput():
        try:
            return map(int, [subprocess.check_output(['tput', 'lines'],stderr=subprocess.STDOUT), subprocess.check_output(['tput', 'cols'])])
        except:
            pass

    return get_terminal_size_stty() or get_terminal_size_tput() or (25, 80)


class OpMode(Enum):
    """Operational Mode"""

    TRAVERSE = auto()
    COMPARE = auto()


class Display(tqdm):
    """
    Handle dispaly while using a progress bar

    Based on tqdm with the following additions:
    - Changed a few defaults
    - Added a different message on close
    - Provide a buffered echo function which buffers output until the bar has finished
    """

    BAR_FORMAT_COMPARE_BASE = '{l_bar}{bar}| {n_fmt}/{total_fmt} '

    def __init__(self, iterable=None, mode: OpMode = None, **kwargs):
        self.mode = mode

        # Holds the output messages which cannot be dispalyed
        # while the progressbar is growing
        self.echo_buffer = []

        _, columns = get_terminal_size()
        ncols = min(columns, 80) - 5
        defaults = {'ascii': True, 'ncols': ncols, 'smoothing': 0}
        if mode == OpMode.TRAVERSE:
            defaults['desc'] = 'Traverse'
            defaults['bar_format'] = "{desc}: {n_fmt} items | {elapsed}s elapsed"
        if mode == OpMode.COMPARE:
            defaults['desc'] = 'Compare'
            defaults['bar_format'] = (
                self.BAR_FORMAT_COMPARE_BASE
                + "{elapsed}s elapsed ({remaining}s remain)"
            )
        for k in defaults:
            if not k in kwargs:
                kwargs[k] = defaults[k]

        return super(Display, self).__init__(iterable, **kwargs)

    def close(self):
        """
        Close the progress bar

        Has a changed Progressbar message + flushes echo buffer
        """
        if self.mode == OpMode.TRAVERSE:
            self.bar_format = "{desc}: {n_fmt} items | {elapsed}s total"
        if self.mode == OpMode.COMPARE:
            self.bar_format = self.BAR_FORMAT_COMPARE_BASE + "{elapsed}s total" + " " * 18
        # We have to save wait state before super.close(),
        # because super.close() changes self.disable
        wait = not self.disable
        super(Display, self).close()
        if wait:
            time.sleep(0.5)
        self.flush_buffer()

    def echo(self, msg):
        """Buffer output if progress bar is running """
        if self.disable:
            click.echo(msg)
        else:
            self.echo_buffer.append(msg)

    def flush_buffer(self):
        """Flush the saved messages to screen"""
        for msg in self.echo_buffer:
            click.echo(msg)
        self.echo_buffer = []
