"""
Utility classes for cmpdisktree
"""

from enum import Enum, auto
from pathlib import Path
from typing import List, TextIO


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


LOG_BACKUP_EXT = '.bak'


class LogFile:
    """
    Write information to a log file

    Features:
    - File is ONLY created when first written to
    - Possible old file (from previous run) is ALWAYS move to *.bak
    """

    def __init__(self, fname: str):
        self.fname = fname
        self.fobject = None
        pf = Path(fname)
        if pf.is_file():
            pf.rename(pf.with_name(pf.name + LOG_BACKUP_EXT))

    def close_if_needed(self):
        """Close file"""
        if self.fobject:
            return self.fobject.close()

    def write(self, txt: str):
        if not self.fobject:
            self.fobject = open(self.fname, 'w')
        print(txt, file=self.fobject)
