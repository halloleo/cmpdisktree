"""
Common definitions (in future) shared between cmpdisktree and cdtlog

Note: For now they are just _copied_ from the relevant file ('utils.py') in cmpdisktree
"""

from enum import Enum, auto


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
