from __future__ import with_statement

import os
import sys

from incoming import __version__
from setuptools import setup, find_packages

install_requires = []
if sys.version_info <= (2, 6):
    install_requires.append('simplejson')

description = ''

path = lambda fname: os.path.join(os.path.dirname(__file__), fname)
for file_ in ('README.rst', 'LICENSE'):
    with open(path('%s' % file_)) as f:
        description += f.read() + '\n\n'

classifiers = ["Programming Language :: Python"]


setup(name='incoming',
      version=__version__,
      url='https://github.com/vaidik/incoming',
      packages=find_packages(),
      long_description=description,
      description=("JSON validation framework for Python."),
      author="Vaidik Kapoor",
      author_email="kapoor.vaidik@gmail.com",
      include_package_data=True,
      zip_safe=False,
      classifiers=classifiers,
      install_requires=install_requires,
      test_suite='incoming.tests')
