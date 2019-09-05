"""
Utility functions for cmpdisktree tests
"""

from pathlib import Path

from cmpdisktree import main


def file_has_lines(fname, num_lines):
    """
    Helper:
    True exactly if file FNAME has exactly NUM_LINES lines
    If num_lines = -1 test that file FNAME does NOT exist
    """
    try:
        max_line_count = num_lines - 1
        with open(fname, 'r') as f:
            for i, l in enumerate(f):
                if i == max_line_count:
                    res = True
                else:  # else occurs before AND after i == max_line_count
                    res = False
        return res
    except FileNotFoundError:
        if num_lines == -1:
            return True
        else:
            raise


def err_log_has_lines(err_lines):
    """Check that err output file has the correct number of lines"""
    return file_has_lines(main.ERR_LOG_DEFAULT_NAME, err_lines)


def ok_log_has_lines(ok_lines):
    """Check that err output file has the correct number of lines"""
    return file_has_lines(main.OK_LOG_DEFAULT_NAME, ok_lines)

def join_path_with_checks(base, dir, name= None):
    dirname = name if name else "directory"
    if not dir:
        raise ValueError(f"{dirname} cannot be empty")
    res = Path(base).joinpath(dir)
    if not res.exists():
        dirtext = f"'{res}' ({dirname})" if dir else f"{dirname}"
        raise ValueError(f"{dirtext} needs to exists")
    return res

def compare_in(data_path, fs1, fs2, **kwargs):
    """Run a compare on "filesystems" under data_path"""
    path1 = join_path_with_checks(data_path, fs1, 'fs1')
    path2 = join_path_with_checks(data_path, fs2, 'fs2')
    cc = main.Comparer(path1, path2, **kwargs)
    return cc.work()


def assert_swap_compare(
    status, data_path, fs1, fs2, err_lines=-1, ok_lines=-1, **kwargs
):
    # Normal compare
    assert compare_in(data_path, fs1, fs2, **kwargs) == status
    assert err_log_has_lines(err_lines)
    assert ok_log_has_lines(ok_lines)
    # Swapped compare (should yield the same error stats!)
    assert compare_in(data_path, fs2, fs1, **kwargs) == status
    assert err_log_has_lines(err_lines)
    assert ok_log_has_lines(ok_lines)
