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
    description = 'A GUI wrapper for the Simple Log Watcher'
    keywords = 'swatch, log, tail',
    long_description = read('README'),

    packages = ['snakewatch'],
    
    license = 'BSD',
    classifiers = [
        'Development Status :: 2 - Press-Alpha',
    ]
)
