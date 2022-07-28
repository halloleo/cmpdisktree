"""
invoke Tasks for maintaining the moreman project
"""
import platform
import shutil
from pathlib import Path

from invoke import task

ROOT_DIR = Path(__file__).parent
SETUP_FILE = ROOT_DIR.joinpath("setup.py")
SOURCE_DIR = ROOT_DIR.joinpath("moreman")
PYTHON_DIRS = [str(d) for d in [SOURCE_DIR]]


# pipenv short cut constants
PER = 'pipenv run'


def pe_run(ctx, cmd):
    """
    Run `cmd` inside the virtualenv via `pipenv run`
    """
    ctx.run(f'{PER} {cmd}')

#
# Source code tasks
#
@task(help={'check': "Checks if source is formatted without applying changes"})
def format(c, check=False):
    """
    Format code
    """
    python_dirs_string = " ".join(PYTHON_DIRS)
    # Run black
    black_opts = f'{"--check" if check else ""}'
    pe_run(c, f'black {black_opts} {python_dirs_string}')
    # Run isort
    isort_opts = f'--recursive {"--check-only" if check else ""}'
    pe_run(c, f'isort {isort_opts} {python_dirs_string}')


@task(help={'part': "Specify version number part (default: 'patch')"})
def newver(c, part='patch'):
    """
    Bump version number
    """
    opts = '--allow-dirty --verbose'
    pe_run(c, f'bumpversion {opts} {part}')

    
#
# Cleaning tasks
#
@task
def clean_build(c):
    """
    Clean up files from package building
    """
    pe_run(c, "rm -fr build/")
    pe_run(c, "rm -fr dist/")
    pe_run(c, "rm -fr .eggs/")
    pe_run(c, "find . -name '*.egg-info' -exec rm -fr {} +")
    pe_run(c, "find . -name '*.egg' -exec rm -f {} +")


@task
def clean_python(c):
    """
    Clean up python file artifacts
    """
    pe_run(c, "find . -name '*.pyc' -exec rm -f {} +")
    pe_run(c, "find . -name '*.pyo' -exec rm -f {} +")
    pe_run(c, "find . -name '*~' -exec rm -f {} +")
    pe_run(c, "find . -name '__pycache__' -exec rm -fr {} +")

    
@task(pre=[clean_build, clean_python])
def clean(c):
    """
    Runs all clean sub-tasks
    """
    pass


#
# Release tasks
#
@task(clean)
def dist(c):
    """
    Build source and wheel packages
    """
    pe_run(c, "python setup.py sdist")
    pe_run(c, "python setup.py bdist_wheel")


@task(pre=[clean, dist])
def publish(c):
    """
    Publish a release of the python package on PyPI
    """
    pe_run(c, "twine upload dist/*")
