"""
Test for the "filesystems in the `symlinks` folder
"""

from pathlib import Path
import pytest

from tests.tutils import assert_swap_compare


DATA_PATH = Path('symlinks')


def test_dir_symlink_same():
    assert_swap_compare(0, DATA_PATH, 'a-dir-symlink', 'b-dir-symlink')

def test_dir_not_symlink():
    assert_swap_compare(1, DATA_PATH, 'a-dir-symlink', 'b-dir-not-symlink', 1)

def test_dir_other_symlink():
    assert_swap_compare(1, DATA_PATH, 'a-dir-symlink', 'b-dir-other-symlink', 1)

def test_file_symlink_same():
    assert_swap_compare(0, DATA_PATH, 'a-file-symlink', 'b-file-symlink')

def test_file_not_symlink():
    assert_swap_compare(1, DATA_PATH, 'a-file-symlink', 'b-file-not-symlink', 1)

def test_file_missing_symlink():
    assert_swap_compare(1, DATA_PATH, 'a-file-symlink', 'b-file-missing-symlink', 1)

