#!/usr/bin/env python
#
# Copyright (c) 2013 Oleksandr Sviridenko
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

import os

from les.utils import unittest

DEFAULT_VERBOSITY_LEVEL = 2
TEST_FILE_SUFFIX = '*_test.py'
TOP_DIR = os.path.dirname(os.path.realpath(__file__))
SRC_DIR = os.path.join(TOP_DIR, 'src', 'main', 'python')

def make_testsuite():
  """Returns test suite."""
  return unittest.TestLoader().discover(SRC_DIR, TEST_FILE_SUFFIX)

def run_tests():
  suite = make_testsuite()
  unittest.TextTestRunner(verbosity=DEFAULT_VERBOSITY_LEVEL).run(suite)

def main():
  run_tests()
  return 0

if __name__ == '__main__':
  exit(main())
