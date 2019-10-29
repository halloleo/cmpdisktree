"""
Test for the "filesystems in the `exclude` folder
"""

from pathlib import Path

from tests.tutils import assert_swap_compare


DATA_PATH = Path('exclude')


class TestWithStdExclude:
    def test_top_here(self):
        assert_swap_compare(
            True,
            DATA_PATH,
            'a-fs-top-here',
            'b-fs-top-here-inside-less+changed-entries',
        )

    def test_rel_top(self):
        # Should give error with default settings
        assert_swap_compare(
            False,
            DATA_PATH,
            'a-rel-fs-top',
            'b-rel-fs-top-inside-less+changed-entries',
            2,
        )

    def test_rel_top_relative_allowed(self):
        assert_swap_compare(
            True,
            DATA_PATH,
            'a-rel-fs-top',
            'b-rel-fs-top-inside-less+changed-entries',
            relative_fs_top=True,
        )

    def test_spaced_mobdoc_and_alias(self):
        assert_swap_compare(
            True,
            DATA_PATH,
            'a-with-spaced-mobdoc-and-alias',
            'b-with-spaced-mobdoc-no-alias',
        )

    def test_added_DSstores(self):
        assert_swap_compare(
            False, DATA_PATH, 'a-fs-top-here', 'b-fs-top-here-added-DSstores', 3
        )


class TestNoStdExclude:

    # Number of errors for the first tests
    ERRORS_IN_FS = 3

    def test_top_here(self):
        # Should give error, because changes are not excluded
        assert_swap_compare(
            False,
            DATA_PATH,
            'a-fs-top-here',
            'b-fs-top-here-inside-less+changed-entries',
            self.ERRORS_IN_FS,
            clear_std_exclusions=True,
        )

    def test_rel_top(self):
        # Should give the same number of error as top_here
        assert_swap_compare(
            False,
            DATA_PATH,
            'a-rel-fs-top',
            'b-rel-fs-top-inside-less+changed-entries',
            self.ERRORS_IN_FS,
            clear_std_exclusions=True,
        )

    def test_rel_top_relative_allowed(self):
        # Should give the same number of error as top_here
        assert_swap_compare(
            False,
            DATA_PATH,
            'a-rel-fs-top',
            'b-rel-fs-top-inside-less+changed-entries',
            self.ERRORS_IN_FS,
            clear_std_exclusions=True,
            relative_fs_top=True,
        )

    # some other tests
    def test_spaced_mobdoc_and_alias(self):
        assert_swap_compare(
            False,
            DATA_PATH,
            'a-with-spaced-mobdoc-and-alias',
            'b-with-spaced-mobdoc-no-alias',
            1,
            clear_std_exclusions=True,
        )

    def test_added_DSstores(self):
        # Should be one Not exist error more than with std exclusions
        assert_swap_compare(
            False,
            DATA_PATH,
            'a-fs-top-here',
            'b-fs-top-here-added-DSstores',
            5,
            clear_std_exclusions=True,
        )


class TestWithLiveExclude:
    def test_added_DSstores(self):
        # Should be one Not exist error more than with std exclusions
        assert_swap_compare(
            True,
            DATA_PATH,
            'a-fs-top-here',
            'b-fs-top-here-added-DSstores',
            live_fs_exclusions=True,
        )
