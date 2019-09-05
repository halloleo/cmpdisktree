"""
Test for the click cli
"""

from pathlib import Path

from click import testing as ctesting

from cmpdisktree import main

DATA_PATH = Path('basic')


def test_help():
    runner = ctesting.CliRunner()
    res = runner.invoke(main.main, ['--help'])
    assert res.exit_code == 0
    assert 'Compare' in res.output
    assert 'macOS disk structure' in res.output


def test_option_handling():
    """Do a run over the "basic" filesystem to check whether options carry through"""
    runner = ctesting.CliRunner()
    fs1 = str(DATA_PATH.joinpath('a'))
    fs2 = str(DATA_PATH.joinpath('b'))
    res = runner.invoke(main.main, [fs1, fs2])
    assert res.exception == None
    assert res.exit_code == 0
