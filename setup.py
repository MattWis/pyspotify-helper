#!/usr/bin/env python
from setuptools import setup

setup(name='pyspotify_helper',
      version='0.0.1',
      author='Matt Wismer',
      author_email='mattwis86@gmail.com',
      description='Simplest integration of Spotify into Python',
      license='MIT',
      packages=['pyspotify_helper'],
      package_dir={'pyspotify_helper': 'pyspotify_helper'},
      url='https://github.com/MattWis/pyspotify_helper.git',
      install_requires=['pyspotify'])
