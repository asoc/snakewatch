#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

import os
from setuptools import setup, find_packages

from snakewatch import NAME, VERSION, DESCRIPTION, URL, AUTHOR, AUTHOR_EMAIL

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

main = ['snakewatch/main.py',]

required_packages = ['colorama', 'argparse', 'importlib', 'pkgutil',]
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
    name = NAME,
    version = VERSION,
    
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    
    url = URL,
    description = DESCRIPTION,
    keywords = 'log, tail',
    long_description = read('README.textile'),

    packages = find_packages(),
    install_requires = need_to_install,
    
    entry_points = {
        'console_scripts': [
            'snakewatch = snakewatch.main:main',
        ],
    },

    license = 'LGPL',
    classifiers = [
        'Development Status :: 4 - Beta',
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
