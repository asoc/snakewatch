#!/usr/bin/env python

import os
from setuptools import setup
from snakewatch.snakewatch import NAME, VERSION, DESCRIPTION

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = NAME,
    version = VERSION,
    
    author = 'Alex Honeywell',
    author_email = 'alex.honeywell@gmail.com',
    
    url = 'http://bitbucket.org/asoc/snakewatch',
    description = DESCRIPTION,
    keywords = 'log, tail',
    long_description = read('README'),

    packages = ['snakewatch'],
    install_requires = ['colorama',],
    
    license = 'LGPL',
    classifiers = [
        'Development Status :: 2 - Press-Alpha',
    ]
)
