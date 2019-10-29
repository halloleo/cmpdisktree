"""
Test for the "filesystems in the `basic` folder
"""

from pathlib import Path

from tests.tutils import assert_swap_compare


DATA_PATH = Path('basic')


class TestFSBasic:
    def test_same(self):
        assert_swap_compare(True, DATA_PATH, 'a', 'b')

    def test_dir_file_diff(self):
        assert_swap_compare(False, DATA_PATH, 'a', 'b-file-diff', 1)

    def test_dir_nonexists(self):
        assert_swap_compare(False, DATA_PATH, 'a', 'b-dir-nonexist', 1)

    def test_file_nonexists(self):
        assert_swap_compare(False, DATA_PATH, 'a', 'b-file-nonexist', 1)


class TestFSBasicStructureOnly:
    def test_same(self):
        assert_swap_compare(True, DATA_PATH, 'a', 'b', traversal_only=True)

    def test_dir_file_diff(self):
        assert_swap_compare(True, DATA_PATH, 'a', 'b-file-diff', traversal_only=True)

    def test_dir_nonexists(self):
        assert_swap_compare(
            False, DATA_PATH, 'a', 'b-dir-nonexist', 1, traversal_only=True
        )

    def test_file_nonexists(self):
        assert_swap_compare(
            False, DATA_PATH, 'a', 'b-file-nonexist', 1, traversal_only=True
        )
