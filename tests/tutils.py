"""
Utility functions for cmpdisktree tests
"""

from pathlib import Path

from cmpdisktree import comparer
from cmpdisktree import utils


def num_of_lines(fname, expected):
    """
    Count number of lines in file to an expected number plus a few
    :param fname: Name of file to count lines
    :param expected: maxmim - usally teh expected number of lines
    :return: Number of lines in file or -1
    """
    try:
        max_line_count = expected + 2
        with open(fname, 'r') as f:
            cnt =0
            for i, l in enumerate(f):
                cnt = i
                if i >  max_line_count:
                    break
        return cnt + 1
    except FileNotFoundError:
        if expected == -1:
            return expected
        else:
            raise


def num_of_err_lines(err_lines):
    """Check that err output file has the correct number of lines"""
    return num_of_lines(utils.ERR_LOG_DEFAULT_NAME, err_lines)


def num_of_ok_lines(ok_lines):
    """Check that err output file has the correct number of lines"""
    return num_of_lines(utils.OK_LOG_DEFAULT_NAME, ok_lines)


def join_path_with_checks(base, dir, name= None):
    dirname = name if name else "directory"
    if not dir:
        raise ValueError(f"{dirname} cannot be empty")
    res = Path(base).joinpath(dir)
    if not res.exists():
        dirtext = f"'{dir}' ({dirname})" if dir else f"{dirname}"
        raise ValueError(f"{dirtext} needs to exists")
    return res


def compare_in(data_path, fs1, fs2, **kwargs):
    """Run a compare on "filesystems" under data_path"""
    path1 = join_path_with_checks(data_path, fs1, 'fs1')
    path2 = join_path_with_checks(data_path, fs2, 'fs2')
    cc = comparer.Comparer(path1, path2, **kwargs)
    return cc.work()


def assert_swap_compare(
    status, data_path, fs1, fs2, err_lines=-1, ok_lines=-1, **kwargs
):
    # Normal compare
    assert compare_in(data_path, fs1, fs2, **kwargs) == status
    assert num_of_err_lines(err_lines) == err_lines
    assert num_of_ok_lines(ok_lines) == ok_lines
    # Swapped compare (should yield the same error stats!)
    assert compare_in(data_path, fs2, fs1, **kwargs) == status
    assert num_of_err_lines(err_lines) == err_lines
    assert num_of_ok_lines(ok_lines) == ok_lines
