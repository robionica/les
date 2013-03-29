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

import numpy
import unittest

from les.problems import BILPProblem
from les.decomposers.finkelstein_qb_decomposer import FinkelsteinQBDecomposer
from les.solvers.symphony_proxy_solver import SymphonyProxySolver

from .local_elimination_solver import LocalEliminationSolver
from .data_models.sqlite_data_model import SQLiteDataModel

class LocalEliminationSolverTest(unittest.TestCase):

  def test_solve1(self):
    cons_matrix = numpy.matrix([[2., 3., 4., 1., 0., 0., 0., 0., 0.],
                                [1., 2., 3., 2., 0., 0., 0., 0., 0.],
                                [0., 0., 1., 4., 3., 4., 2., 0., 0.],
                                [0., 0., 2., 1., 1., 2., 5., 0., 0.],
                                [0., 0., 0., 0., 0., 0., 2., 1., 2.],
                                [0., 0., 0., 0., 0., 0., 3., 4., 1.]])
    problem = BILPProblem([8, 2, 5, 5, 8, 3, 9, 7, 6],
                          True,
                          cons_matrix,
                          None,
                          [7, 6, 9, 7, 3, 5])
    decomposer = FinkelsteinQBDecomposer()
    decomposer.decompose(problem)
    solver = LocalEliminationSolver(master_solver=SymphonyProxySolver,
                                    data_model=SQLiteDataModel())
    solver.load_problem(problem, decomposer.get_decomposition_tree())
    solver.solve()
    self.assertEqual(39.0, solver.get_obj_value())

  def test_solve2(self):
    cons_matrix = numpy.matrix([[3., 4., 1., 0., 0., 0., 0.],
                                [0., 2., 3., 3., 0., 0., 0.],
                                [0., 2., 0., 0., 3., 0., 0.],
                                [0., 0., 2., 0., 0., 3., 2.]])
    problem = BILPProblem([2, 3, 1, 5, 4, 6, 1],
                          True,
                          cons_matrix,
                          None,
                          [6, 5, 4, 5])
    decomposer = FinkelsteinQBDecomposer()
    decomposer.decompose(problem)
    subproblems = decomposer.get_decomposition_tree().get_subproblems()
    solver = LocalEliminationSolver(master_solver=SymphonyProxySolver,
                                    data_model=SQLiteDataModel())
    solver.load_problem(problem, decomposer.get_decomposition_tree())
    solver.solve()
    self.assertEqual(18.0, solver.get_obj_value())

if __name__ == "__main__":
  unittest.main()
