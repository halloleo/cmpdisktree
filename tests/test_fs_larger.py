"""
Test for the "filesystems in the `basic` folder
"""

from pathlib import Path

from tests.tutils import assert_swap_compare

DATA_PATH = Path('larger')


class TestFSLarger:
    def test_same(self):
        assert_swap_compare(True, DATA_PATH, 'one', 'two')

    def test_file_diff(self):
        assert_swap_compare(False, DATA_PATH, 'one', 'two-3-files-diff', 3)

    def test_dir_diff(self):
        # Note: Here we have in total 3 different lines, because the 1 renamed dir
        # 'moreman-other-name' results in a 'Directory does not exist in FS2' line
        # AND a 'Directory does not exist in FS1' line, so in 2 lines.
        assert_swap_compare(False, DATA_PATH, 'one', 'two-2-dirs-diff', 3)


class TestFSLargerStructureOnly:
    def test_same(self):
        assert_swap_compare(True, DATA_PATH, 'one', 'two', traversal_only=True)

    def test_file_diff(self):
        assert_swap_compare(True, DATA_PATH, 'one', 'two-3-files-diff',
                            traversal_only=True)

    def test_dir_diff(self):
        # Note: Here we have in total 3 different lines, because the 1 renamed dir
        # 'moreman-other-name' results in a 'Directory does not exist in FS2' line
        # AND a 'Directory does not exist in FS1' line, so in 2 lines.
        assert_swap_compare(False, DATA_PATH, 'one', 'two-2-dirs-diff', 3,
                            traversal_only=True)
