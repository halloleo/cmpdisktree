"""
Test for the "filesystems in the `exclude` folder
"""

from pathlib import Path
import pytest

from tests.tutils import assert_swap_compare


DATA_PATH = Path('exclude')


def test_with_standard_exclude():
    assert_swap_compare(0, DATA_PATH, 'a', 'b')

def test_same_without_Standard_exclude():
    assert_swap_compare(1, DATA_PATH, 'a', 'b', 2,
                        clear_standard_exclusions=True)
