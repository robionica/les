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

import numpy as np
import unittest

from les.problems.bilp_problem import BILPProblem
from les.ext.coin.osi_sym_solver_interface import OsiSymSolverInterface

class OsiSymSolverInterfaceTest(unittest.TestCase):

  def test_solve1(self):
    cons_matrix = np.matrix([[2., 3., 4., 1., 0., 0., 0., 0., 0.],
                             [1., 2., 3., 2., 0., 0., 0., 0., 0.],
                             [0., 0., 1., 4., 3., 4., 2., 0., 0.],
                             [0., 0., 2., 1., 1., 2., 5., 0., 0.],
                             [0., 0., 0., 0., 0., 0., 2., 1., 2.],
                             [0., 0., 0., 0., 0., 0., 3., 4., 1.],
                             ])
    problem = BILPProblem([8, 2, 5, 5, 8, 3, 9, 7, 6],
                          True,
                          cons_matrix,
                          None,
                          [7, 6, 9, 7, 3, 5])
    solver = OsiSymSolverInterface()
    solver.load_problem(problem)
    solver.solve()
    self.assertEqual(39.0, solver.get_obj_value())
    col_solution = [1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0]
    for i in range(len(col_solution)):
      self.assertEqual(col_solution[i], solver.get_col_solution()[i])

  def test_solve2(self):
    problem = BILPProblem([2.0], True, np.matrix([[3.0]]), None, [1.0])
    solver = OsiSymSolverInterface()
    solver.load_problem(problem)
    solver.solve()

if __name__ == "__main__":
  unittest.main()
