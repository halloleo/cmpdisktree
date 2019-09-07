"""
Test for the "filesystems in the `basic` folder
"""

from pathlib import Path

from tests.tutils import (
    assert_swap_compare,
)


DATA_PATH = Path('basic')


class TestFSBasic:
    def test_same(self):
        assert_swap_compare(0, DATA_PATH, 'a', 'b')

    def test_dir_file_diff(self):
        assert_swap_compare(1, DATA_PATH, 'a', 'b-file-diff', 1)

    def test_dir_nonexists(self):
        assert_swap_compare(1, DATA_PATH, 'a', 'b-dir-nonexist', 1)

    def test_file_nonexists(self):
        assert_swap_compare(1, DATA_PATH, 'a', 'b-file-nonexist', 1)


class TestFSBasicStructureOnly:
    def test_same(self):
        assert_swap_compare(0, DATA_PATH, 'a', 'b', structure_only=True)

    def test_dir_file_diff(self):
        assert_swap_compare(0, DATA_PATH, 'a', 'b-file-diff', structure_only=True)

    def test_dir_nonexists(self):
        assert_swap_compare(1, DATA_PATH, 'a', 'b-dir-nonexist', 1, structure_only=True)

    def test_file_nonexists(self):
        assert_swap_compare(
            1, DATA_PATH, 'a', 'b-file-nonexist', 1, structure_only=True
        )
