# -*- coding: utf-8; -*-
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

from __future__ import with_statement

import os
import unittest

from les.problems.bilp_problem import BILPProblem
from les.readers.mps_reader import MPSReader

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "bilp_problem_test_data")

class BILPProblemTest(unittest.TestCase):

  def test_build_from_mps(self):
    test_filename = os.path.join(TEST_DATA_DIR, "test.mps")
    reader = MPSReader()
    with open(test_filename, "r") as stream:
      reader.parse(stream)
    problem = BILPProblem.build(reader)
    self.assertEqual(7, problem.get_num_cols())
    self.assertEqual(4, problem.get_num_rows())

if __name__ == "__main__":
  unittest.main()
