"""
Test for the "filesystems in the `basic` folder
"""

from pathlib import Path

from tests.tutils import assert_swap_compare, join_path_with_checks

DATA_PATH = Path('basic')


class TestTravListBasic:
    def test_same_in_diff(self):
        travpath = join_path_with_checks(DATA_PATH, 'png-only-list.txt',
                                        'traverse_from_list')
        assert_swap_compare(True, DATA_PATH, 'a', 'b-file-diff',
                            traverse_from_list=travpath)

    def test_diff_in_diff(self):
        travpath = join_path_with_checks(DATA_PATH, 'file-txt-only-list.txt',
                                        'traverse_from_list')
        assert_swap_compare(False, DATA_PATH, 'a', 'b-file-diff', 1,
                            traverse_from_list=travpath)
