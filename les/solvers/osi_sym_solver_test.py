#!/usr/bin/env python
#
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

from les.problems.bilp_problem import BILPProblem
from les.solvers.osi_sym_solver import OsiSymSolver
from les.utils import unittest

class OsiSymSolverTest(unittest.TestCase):

  def setUp(self):
    self.si = OsiSymSolver()
    self.si.set_sym_param("verbosity", -2)

  def test_solve1(self):
    problem = BILPProblem('P', (
        [8, 2, 5, 5, 8, 3, 9, 7, 6],
        [[2., 3., 4., 1., 0., 0., 0., 0., 0.],
         [1., 2., 3., 2., 0., 0., 0., 0., 0.],
         [0., 0., 1., 4., 3., 4., 2., 0., 0.],
         [0., 0., 2., 1., 1., 2., 5., 0., 0.],
         [0., 0., 0., 0., 0., 0., 2., 1., 2.],
         [0., 0., 0., 0., 0., 0., 3., 4., 1.]],
        ['L'] * 6,
        [7, 6, 9, 7, 3, 5]
    ))
    self.si.load_problem(problem)
    self.si.solve()
    self.assert_equal(39.0, self.si.get_obj_value())
    col_solution = [1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0]
    for i in range(len(col_solution)):
      self.assert_equal(col_solution[i], self.si.get_col_solution()[i])

  def test_solve2(self):
    problem = BILPProblem.build_from_scratch([2.0], [[3.0]], ['L'], [1.0])
    self.si.load_problem(problem)
    self.si.solve()

if __name__ == '__main__':
  unittest.main()
