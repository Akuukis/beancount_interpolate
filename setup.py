#!/usr/bin/env python

from distutils.core import setup

setup(
    name='beancount-interpolate',
    version='2.0.5',
    description='Plugins for Beancount to interpolate transactions',
    long_description=
    """
Four plugins for double-entry accounting system Beancount to interpolate transactions by generating additional entries over time.

- **recur**: dublicates all entry postings over time
- **split**: dublicates all entry postings over time at fraction of value
- **depr**: generates new entries over time to depreciate source postings
- **spread**: same as **depr** but for *Income* and *Expenses* postings

These plugins are triggered by adding metadata or tags to source entries. It's safe to disable at any time. All plugins share the same parser that can set maximal period, custom starting date and minimal step by either number or keyword.

You can use these to define recurring transactions, account for depreciation, smooth transactions over time and make graphs less zig-zag.
    """,
    license='GNU GPLv3',
    author='Kalvis \'Akuukis\' Kalnins',
    author_email='akuukis@kalvis.lv',
    url='https://github.com/Akuukis/beancount-interpolate',
    download_url='https://pypi.python.org/pypi/beancount-interpolate',
    package_dir={'beancount-interpolate': 'src'},
    packages=['beancount-interpolate'],
    package_data={'beancount-interpolate': ['../README.md']},
    requires=['beancount (>2.0)'],
     )
