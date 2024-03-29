"""
Test for the "filesystems in the `symlinks` folder

Note: The `symlinks` folder is on systems hosting the source code on Dropbox 
      outside the git system.
"""

from pathlib import Path

from tests.tutils import assert_swap_compare

DATA_PATH = Path('symlinks')
if 'Dropbox' in str(DATA_PATH.absolute().resolve()):
    SECONDARY_TEST_TOP = Path('~/data/devel/files/cmpdisktree')
    DATA_PATH = SECONDARY_TEST_TOP.expanduser().joinpath(DATA_PATH)


class TestFSDirSymlinks:
    def test_dir_symlink_same(self):
        assert_swap_compare(True, DATA_PATH, 'a-dir-symlink', 'b-dir-symlink')

    def test_dir_not_symlink(self):
        assert_swap_compare(False, DATA_PATH, 'a-dir-symlink', 'b-dir-not-symlink', 1)

    def test_dir_other_symlink(self):
        assert_swap_compare(False, DATA_PATH, 'a-dir-symlink', 'b-dir-other-symlink', 1)


class TestFSFileSymlinks:
    def test_file_symlink_same(self):
        assert_swap_compare(True, DATA_PATH, 'a-file-symlink', 'b-file-symlink')

    def test_file_not_symlink(self):
        assert_swap_compare(False, DATA_PATH, 'a-file-symlink', 'b-file-not-symlink', 1)

    def test_file_missing_symlink(self):
        assert_swap_compare(
            False, DATA_PATH, 'a-file-symlink', 'b-file-missing-symlink', 1
        )


class TestFSAbsSymlinks:
    def test_dir_missing_abssymlink(self):
        assert_swap_compare(True, DATA_PATH, 'a-dir-abssymlink', 'b-dir-abssymlink')

    def test_dir_missing_other_abssymlink(self):
        assert_swap_compare(
            False, DATA_PATH, 'a-dir-abssymlink', 'b-dir-other-abssymlink', 1
        )
