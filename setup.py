#!/usr/bin/env python

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
    description = "A Python log watcher",
    keywords = 'log, tail',
    long_description = read('README'),

    packages = ['snakewatch', 'snakewatch.ui', 'snakewatch.input', 'snakewatch.action'],
    install_requires = ['colorama',],
    
    entry_points = {
        'console_scripts': [
            'snakewatch = snakewatch.main:main',
        ],
    },

    license = 'LGPL',
    classifiers = [
        'Development Status :: 2 - Press-Alpha',
    ]
)
