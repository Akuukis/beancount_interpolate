#!/usr/bin/env python

from distutils.core import setup

setup(
	  name='beancount-interpolate',
      version='1.0.0',
      description='Interpolatation plugins for Beancount',
      url='https://github.com/Akuukis/beancount_interpolate',
      author='Kalvis \'Akuukis\' Kalnins',
      author_email='akuukis@kalvis.lv',
      license='GPLv3',
      packages=['beancount-interpolate'],
      package_dir={'beancount-interpolate': 'src'},
      package_data={'beancount-interpolate': ['README.md']},
      requires=['beancount (>2.0)'],
     )
