"""
Test for the "filesystems in the `basic` folder
"""

from pathlib import Path

from tests.tutils import assert_swap_compare, join_path_with_checks

DATA_PATH_BASIC = Path('basic')
DATA_PATH_LARGER = Path('larger')


class TestTravListBasic:
    def test_same_in_diff(self):
        travpath = join_path_with_checks(DATA_PATH_BASIC, 'png-only-list.txt',
                                        'traverse_from_list')
        assert_swap_compare(True, DATA_PATH_BASIC, 'a', 'b-file-diff',
                            traverse_from_list=travpath)

    def test_same_in_diff_with_dot_path(self):
        travpath = join_path_with_checks(DATA_PATH_BASIC,
                                         'png-only-list-as-dot-path.txt',
                                        'traverse_from_list')
        assert_swap_compare(True, DATA_PATH_BASIC, 'a', 'b-file-diff',
                            traverse_from_list=travpath)

    def test_diff_in_diff(self):
        travpath = join_path_with_checks(DATA_PATH_BASIC, 'file-txt-only-list.txt',
                                        'traverse_from_list')
        assert_swap_compare(False, DATA_PATH_BASIC, 'a', 'b-file-diff', 1,
                            traverse_from_list=travpath)

    def test_same_in_nonexist(self):
        travpath = join_path_with_checks(DATA_PATH_BASIC, 'file-txt-only-list.txt',
                                        'traverse_from_list')
        assert_swap_compare(True, DATA_PATH_BASIC, 'a', 'b-file-nonexist',
                            traverse_from_list=travpath)

    def test_nonexist_in_diff(self):
        travpath = join_path_with_checks(DATA_PATH_BASIC, 'nonexist-in-list.txt',
                                        'traverse_from_list')
        assert_swap_compare(False, DATA_PATH_BASIC, 'a', 'b-file-diff', 1,
                            traverse_from_list=travpath)

class TestTravListLarger:
    def test_same_files_in_diff(self):
        travpath = join_path_with_checks(DATA_PATH_LARGER,
                                         'spare-changed-files-list.txt',
                                        'traverse_from_list')
        assert_swap_compare(True, DATA_PATH_LARGER, 'one', 'two-3-files-diff',
                            traverse_from_list=travpath)

    def test_same_files_in_diff(self):
        travpath = join_path_with_checks(DATA_PATH_LARGER,
                                         'spare-changed-files-plus-nonexist-list.txt',
                                        'traverse_from_list')
        assert_swap_compare(False, DATA_PATH_LARGER, 'one', 'two-3-files-diff', 1,
                            traverse_from_list=travpath)
