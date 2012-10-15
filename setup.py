#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'snakewatch',
    version = '0.1.dev',
    
    author = 'Alex Honeywell',
    author_email = 'alex.honeywell@gmail.com',
    
    url = 'http://bitbucket.org/asoc/snakewatch',
    description = 'A Python log watcher',
    keywords = 'log, tail',
    long_description = read('README.txt'),

    packages = ['snakewatch', 'snakewatch.ui', 'snakewatch.input', 'snakewatch.action'],
    install_requires = ['colorama', 'importlib', 'json', 'argparse'],
    
    entry_points = {
        'console_scripts': [
            'snakewatch = snakewatch.main:main',
        ],
    },

    license = 'LGPL',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Library or Lesser General Public License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Logging',
    ]
)
