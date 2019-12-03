"""
Utility functions for cmpdisktree tests
"""

from pathlib import Path

from cmpdisktree import comparer, utils


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
            cnt = 0
            for i, l in enumerate(f):
                cnt = i
                if i > max_line_count:
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


def join_path_with_checks(base, dir, name=None):
    dirname = name if name else "directory"
    if not dir:
        raise ValueError(f"{dirname} cannot be empty")
    res = Path(base).joinpath(dir)
    if not res.exists():
        dirtext = f"'{dir}' ({dirname})" if dir else f"{dirname}"
        raise ValueError(f"{dirtext} needs to exists")
    return res


def compare_in(data_path, fs1, fs2, **kwargs):
    """
    Run a compare on "filesystems" under data_path

    :return: True/false whether compare was ok
    """
    path1 = join_path_with_checks(data_path, fs1, 'fs1')
    path2 = join_path_with_checks(data_path, fs2, 'fs2')
    cc = comparer.Comparer(path1, path2, force_progress=False, **kwargs)
    status = cc.work()
    return status == 0


def assert_swap_compare(
    expected_ok,
    data_path,
    fs1,
    fs2,
    expected_err_lines=-1,
    expected_ok_lines=-1,
    **kwargs,
):
    """Cmpare to FSs a/b and b/a expecing the results should be mirrored"""

    # Normal compare
    actual_ok = compare_in(data_path, fs1, fs2, **kwargs)
    assert actual_ok == expected_ok

    actual_err_lines = num_of_err_lines(expected_err_lines)
    assert actual_err_lines == expected_err_lines

    actual_ok_lines = num_of_ok_lines(expected_ok_lines)
    assert actual_ok_lines == expected_ok_lines

    # Swapped compare (should yield the same error stats!)
    actual_ok = compare_in(data_path, fs2, fs1, **kwargs)
    assert actual_ok == expected_ok

    actual_err_lines = num_of_err_lines(expected_err_lines)
    assert actual_err_lines == expected_err_lines

    actual_ok_lines = num_of_ok_lines(expected_ok_lines)
    assert actual_ok_lines == expected_ok_lines
