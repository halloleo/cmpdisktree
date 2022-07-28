#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Config file for installing/publishing moreman
"""

# For a fully annotated version of this file and what it does, see
# https://github.com/pypa/sampleproject/blob/master/setup.py

import ast
import io
import re
import os
from setuptools import find_packages, setup

DEPENDENCIES = ['argh']
EXCLUDE_FROM_PACKAGES = ['contrib', 'docs', 'tests*']
CURDIR = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(CURDIR, 'README.md'), 'r', encoding='utf-8') as f:
    README = f.read()


def get_version():
    """Version for setup function"""
    main_file = os.path.join(CURDIR, 'moreman', '__init__.py')
    _version_re = re.compile(r'__version__\s+=\s+(?P<version>.*)')
    with open(main_file, 'r', encoding='utf8') as f:
        match = _version_re.search(f.read())
        version = match.group("version") if match is not None else '"unknown"'
    return str(ast.literal_eval(version))


setup(
    name='moreman',
    version=get_version(),
    author='halloleo',
    author_email='moreman@halloleo.hailmail.net',
    description="Man Pages for Commands without Man Pages",
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/halloleo/moreman',
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    keywords=['system', 'man', 'help'],
    scripts=[],
    entry_points={'console_scripts': ['moreman=moreman.main:main']},
    zip_safe=False,
    install_requires=DEPENDENCIES,
    test_suite='tests.test_project',
    python_requires='>=3.6',
    # license and classifier list:
    # https://pypi.org/pypi?%3Aaction=list_classifiers
    license='License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Topic :: System :: Shells',
        'Topic :: Terminals',
        'Topic :: Text Editors :: Emacs',
        'Topic :: Utilities',
    ],
)
