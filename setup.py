"""
This file is part of snakewatch.

snakewatch is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

snakewatch is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with snakewatch.  If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import print_function

import ez_setup
ez_setup.use_setuptools()

import os
import sys
from setuptools import setup, find_packages

from snakewatch import NAME, VERSION, DESCRIPTION, URL, AUTHOR, AUTHOR_EMAIL

main = ['snakewatch/main.py']
required_packages = ['colorama', 'argparse', 'importlib', 'pkgutil']
need_to_install = []

extra_options = dict(
    scripts=main,
)
options = dict()

if 'py2exe' in sys.argv:
    try:
        import py2exe
    except ImportError:
        print('py2exe not found, cannot build executable.', file=sys.stderr)
        sys.exit(1)

    extra_options.update(dict(
        console=main,
        zipfile=None,
    ))

    options['py2exe'] = dict(
        bundle_files=1,
    )


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

for pkg in required_packages:
    try:
        __import__(pkg)
    except ImportError:
        need_to_install.append(pkg)


setup(
    name=NAME,
    version=VERSION,
    
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    
    url=URL,
    description=DESCRIPTION,
    keywords='log, tail',
    long_description=read('README.textile'),

    packages=find_packages(),
    install_requires=need_to_install,
    
    entry_points={
        'console_scripts': [
            'snakewatch = snakewatch.main:main',
        ],
    },

    license='LGPL',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Library or Lesser General Public License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Logging',
    ],

    options=options,
    **extra_options
)
