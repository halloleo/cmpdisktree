"""
Test for classes and functions in utils.py
"""

from pathlib import Path
from cmpdisktree.utils import ErrorKind, FileKind

class TestUtils():

    def test_ErrKind_txt(self):
        assert ErrorKind.NOT_EXIST_IN_1.txt(FileKind.FILE) == \
               "File does not exist in FS1"
        assert ErrorKind.NOT_EXIST_IN_2.txt(FileKind.DIR) == \
               "Directory does not exist in FS2"
        assert ErrorKind.DIFF.txt(FileKind.FILE) == \
               "Content is different"
        assert ErrorKind.DIFF.txt(FileKind.SYMLINK) == \
               "Symlink target is different"
        assert ErrorKind.MISMATCH.txt(FileKind.SYMLINK) == \
               "Node type in FS2 is not Symlink"
        assert ErrorKind.NOACCESS.txt(FileKind.FILE) == \
               "No access to File (e.g. file permissions)"
