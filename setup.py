'''
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
'''

import ez_setup
ez_setup.use_setuptools()

import os
from setuptools import setup, find_packages

from snakewatch import NAME, VERSION, DESCRIPTION, URL, AUTHOR, AUTHOR_EMAIL


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

main = ['snakewatch/main.py']

required_packages = ['colorama', 'argparse', 'importlib', 'pkgutil']
need_to_install = []

for pkg in required_packages:
    try:
        __import__(pkg)
    except ImportError:
        need_to_install.append(pkg)

extra_options = dict(
    scripts = main,
)

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
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Library or Lesser General Public License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Logging',
    ],
    
    **extra_options
)
