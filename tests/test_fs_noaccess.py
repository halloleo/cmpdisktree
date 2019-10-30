"""
Test for the "filesystems" in the `noaccess` folder

Note: The `noaccess` folder is always outside the git system.
"""

from pathlib import Path
import pytest

from tests.tutils import assert_swap_compare


DATA_PATH = Path('noaccess')
SECONDARY_TEST_TOP = Path('~/data/devel/files/cmpdisktree')
DATA_PATH = SECONDARY_TEST_TOP.expanduser().joinpath(DATA_PATH)


class TestAsNormalUser:
    def test_same(self):
        assert_swap_compare(False, DATA_PATH, 'a-dir+file-noaccess', 'b-dir+file-noaccess', 2)

    def test_noaccess_file_changed(self):
        assert_swap_compare(False, DATA_PATH, 'a-dir+file-noaccess', 'b-dir+file-noaccess-file-changed', 2)


@pytest.mark.skip(reason="sudo not yet implemented")
class TestAsRootUser:
    def test_same(self):
        assert_swap_compare(True, DATA_PATH, 'a-dir+file-noaccess', 'b-dir+file-noaccess')

    def test_noaccess_file_changed(self):
        assert_swap_compare(False, DATA_PATH, 'a-dir+file-noaccess', 'b-dir+file-noaccess-file-changed', 1)
