"""
Test for the "filesystems in the `exclude` folder
"""

from pathlib import Path

from tests.tutils import assert_swap_compare


DATA_PATH = Path('exclude')


def test_front_with_std__exclude():
    assert_swap_compare(0, DATA_PATH, 'a-front-exclude', 'b-front-exclude-less+changed-inside')


def test_front_without_std_exclude():
    assert_swap_compare(1, DATA_PATH, 'a-front-exclude', 'b-front-exclude-less+changed-inside', 3, clear_std_exclusions=True)
