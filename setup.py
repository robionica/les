#!/usr/bin/env python
#
# Copyright (c) 2012-2013 Oleksandr Sviridenko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# See http://peak.telecommunity.com/DevCenter/EasyInstall for details.
from bootstrap import use_setuptools

import os
import setuptools
import sys

PYTHON_SRC_DIR = os.path.join('src', 'main', 'python')

def main():
  setuptools.setup(
    author='Oleksandr Sviridenko',
    author_email='oleks.sviridenko@gmail.com',
    classifiers=[
      'License :: OSI Approved :: Apache Software License',
      'Topic :: Scientific/Engineering :: Mathematics'
    ],
    description='Local Elimination Solver',
    install_requires=[
      'networkx',
      'scipy',
      'sympy',
      'numpy',
      'protobuf >= 2.1.0',
      'matplotlib',
    ],
    license='Apache',
    name='les',
    packages=setuptools.find_packages(PYTHON_SRC_DIR),
    package_dir={'': PYTHON_SRC_DIR},
    test_suite='test.make_testsuite',
    version='1.0.0'
  )
  return 0

if __name__ == '__main__':
  sys.exit(main())
