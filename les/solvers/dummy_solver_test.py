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

from les.problems import BILPProblem
from les.solvers.dummy_solver import DummySolver
from les.utils import unittest

class DummySolverTest(unittest.TestCase):

  def test_solve1(self):
    problem = BILPProblem.build_from_scratch(
      [8, 2, 5, 5],
      [[4., 3., 0., 0.], [0., 0., 1., 7.]],
      ['L', 'L'],
      [7, 8])
    solver = DummySolver()
    solver.load_problem(problem)
    solver.solve()
    self.assert_equal(20.0, solver.get_obj_value())
    self.assert_equal([1., 1., 1., 1.], solver.get_col_solution())

  def test_solve2(self):
    problem = BILPProblem('P', (
      [8, 2, 5, 5],
      [[4.,3.,0.,0.], [0.,0.,1.,9.], [0.,2.,1.,9.]],
      ['L', 'L', 'L'],
      [7, 8, 5]
    ))
    solver = DummySolver()
    solver.load_problem(problem)
    solver.solve()
    self.assert_equal(0.0, solver.get_obj_value())
    self.assert_equal([0., 0., 0., 0.], solver.get_col_solution())

if __name__ == '__main__':
  unittest.main()
