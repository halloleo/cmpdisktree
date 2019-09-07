"""
Test for classes and functions in utils.py
"""

from pathlib import Path
import pytest
from cmpdisktree.utils import ErrorKind, FileKind
from tests import tutils


class TestUtils:
    """ Test utils.py (general utility classes)"""
    def test_ErrKind_txt(self):
        assert (
            ErrorKind.NOT_EXIST_IN_1.txt(FileKind.FILE) == "File does not exist in FS1"
        )
        assert (
            ErrorKind.NOT_EXIST_IN_2.txt(FileKind.DIR)
            == "Directory does not exist in FS2"
        )
        assert ErrorKind.DIFF.txt(FileKind.FILE) == "Content is different"
        assert ErrorKind.DIFF.txt(FileKind.SYMLINK) == "Symlink target is different"
        assert (
            ErrorKind.MISMATCH.txt(FileKind.SYMLINK)
            == "Node type in FS2 is not Symlink"
        )
        assert (
            ErrorKind.NOACCESS.txt(FileKind.FILE)
            == "No access to File (e.g. file permissions)"
        )

DATA_PATH = Path('basic')

FIVE_LINE_FNAME = 'five-liner.txt'
@pytest.fixture()
def file_with_5_lines():
    with open(FIVE_LINE_FNAME, 'w') as f:
        for i in range(1,6):
            print(f"Line numero {i}",file=f)
    yield FIVE_LINE_FNAME

class TestTutils:
    """ Test tutils.py (utility functions for tests)"""
    def test_join_path_with_checks(self):
        with pytest.raises(ValueError):
            assert tutils.join_path_with_checks(DATA_PATH, '')

        with pytest.raises(ValueError):
            assert tutils.join_path_with_checks(DATA_PATH, 'does_not_exist')

        assert tutils.join_path_with_checks(DATA_PATH, 'a') == DATA_PATH.joinpath('a')

    def test_num_of_lines(self, file_with_5_lines):
        assert tutils.num_of_lines(FIVE_LINE_FNAME, 5) == 5

    def test_num_of_lines_nonexisting(self):
        assert tutils.num_of_lines('expected-nonexisting.txt', -1) == -1
        with pytest.raises(FileNotFoundError):
            assert tutils.num_of_lines('unexpected-nonexisting.txt', 15) == 15

