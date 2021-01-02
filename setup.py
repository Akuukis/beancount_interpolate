#!/usr/bin/env python3

from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='beancount_interpolate',
    version='2.1.6',
    description='Plugins for Beancount to interpolate transactions',

    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Akuukis',
    author_email='akuukis@kalvis.lv',
    download_url='https://pypi.python.org/pypi/beancount_interpolate',
    license='GNU GPLv3',
    package_data={'beancount_interpolate': ['../README.md']},
    package_dir={'beancount_interpolate': 'beancount_interpolate'},
    packages=['beancount_interpolate'],
    requires=['beancount (>2.0)', 'beancount_plugin_utils'],
    url='https://github.com/Akuukis/beancount_interpolate',
)
