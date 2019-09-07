"""
Test for the "filesystems in the `exclude` folder
"""

from pathlib import Path

from tests.tutils import assert_swap_compare


DATA_PATH = Path('exclude')


class TestWithStdExclude:
    def test_top_here(self):
        assert_swap_compare(
            0, DATA_PATH, 'a-fs-top-here', 'b-fs-top-here-inside-less+changed-entries'
        )

    def test_rel_top(self):
        # Should give error with default settings
        assert_swap_compare(
            1, DATA_PATH, 'a-rel-fs-top', 'b-rel-fs-top-inside-less+changed-entries',2
        )

    def test_rel_top_relative_allowed(self):
        assert_swap_compare(
            0, DATA_PATH, 'a-rel-fs-top', 'b-rel-fs-top-inside-less+changed-entries',
            relative_fs_top=True
        )

    def test_spaced_mobdoc_and_alias(self):
        assert_swap_compare(
            0, DATA_PATH, 'a-with-spaced-mobdoc-and-alias', 'b-with-spaced-mobdoc-no-alias',
        )

class TestNoStdExclude:

    ERRORS_IN_FS = 3

    def test_top_here(self):
        # Should give error, because changes are not excluded
        assert_swap_compare(
            1,
            DATA_PATH,
            'a-fs-top-here',
            'b-fs-top-here-inside-less+changed-entries',
            self.ERRORS_IN_FS,
            clear_std_exclusions=True,
        )

    def test_rel_top(self):
        # Should give the same number of error as top_here
        assert_swap_compare(
            1, DATA_PATH, 'a-rel-fs-top', 'b-rel-fs-top-inside-less+changed-entries',self.ERRORS_IN_FS,
            clear_std_exclusions = True,
        )

    def test_rel_top_relative_allowed(self):
        # Should give the same number of error as top_here
        assert_swap_compare(
            1, DATA_PATH, 'a-rel-fs-top', 'b-rel-fs-top-inside-less+changed-entries', self.ERRORS_IN_FS,
            clear_std_exclusions = True,
            relative_fs_top=True
        )

    def test_spaced_mobdoc_and_alias(self):
        assert_swap_compare(
            1, DATA_PATH, 'a-with-spaced-mobdoc-and-alias', 'b-with-spaced-mobdoc-no-alias', 1,
            clear_std_exclusions=True,
            )
