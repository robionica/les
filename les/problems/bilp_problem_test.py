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

import operator
import os

from les.problems.bilp_problem import BILPProblem
from les.readers.mps_reader import MPSReader
from les.utils import unittest

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "bilp_problem_test_data")

class BILPProblemTest(unittest.TestCase):

  def test_set_constraints(self):
    problem = BILPProblem()
    lhs = [[1, 2, 3], [4, 5, 6]]
    senses = ['L', 'L']
    rhs = [3, 9]
    problem.set_constraints(lhs, senses, rhs)
    self.assert_equal(2, problem.get_num_constraints())
    self.assert_equal(3, problem.get_num_variables())
    for i in range(len(rhs)):
      self.assert_equal(rhs[i], problem.get_rhs()[i])
    for i in range(len(lhs)):
      for j in range(len(lhs[i])):
        self.assert_equal(lhs[i][j], problem.get_lhs()[i,j])

  def test_read_problem_from_scratch(self):
    problem = BILPProblem("PROBLEM",(
        ([8, 2, 5, 5, 8, 3, 9, 7, 6], True),
        [[2., 3., 4., 1., 0., 0., 0., 0., 0.],
         [1., 2., 3., 2., 0., 0., 0., 0., 0.],
         [0., 0., 1., 4., 3., 4., 2., 0., 0.],
         [0., 0., 2., 1., 1., 2., 5., 0., 0.],
         [0., 0., 0., 0., 0., 0., 2., 1., 2.],
         [0., 0., 0., 0., 0., 0., 3., 4., 1.]],
        [operator.le] * 6,
        [7, 6, 9, 7, 3, 5])
    )
    self.assert_equal(9, problem.get_num_columns())

  def test_build_from_mps(self):
    test_filename = os.path.join(TEST_DATA_DIR, "test.mps")
    reader = MPSReader()
    with open(test_filename, "r") as stream:
      reader.parse(stream)
    problem = BILPProblem.build(reader)
    self.assert_equal(7, problem.get_num_variables())
    self.assert_equal(4, problem.get_num_constraints())

  def test_check_col_solution(self):
    test_filename = os.path.join(TEST_DATA_DIR, "test.mps")
    reader = MPSReader()
    with open(test_filename, "r") as stream:
      reader.parse(stream)
    problem = BILPProblem.build(reader)
    self.assert_false(problem.check_col_solution([1., 1., 1., 1., 1., 1., 1.]))
    self.assert_true(problem.check_col_solution([1., 0., 0., 1., 1., 1., 1.]))

if __name__ == '__main__':
  unittest.main()
