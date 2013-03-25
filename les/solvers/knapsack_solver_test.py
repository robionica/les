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

import unittest

from les.solvers.knapsack_solver import KnapsackProblem, FractionalKnapsackSolver

class FractionalKnapsackSolverTest(unittest.TestCase):

  def test_solve(self):
    v = [8, 11, 6, 4]
    w = [5,  7, 4, 3]
    W = 14
    solution = [1.0, 1.0, 0.5, 0.0]
    value = sum([float(v[i]) * solution[i] for i in range(len(v))])
    problem = KnapsackProblem(v, w, W)
    solver = FractionalKnapsackSolver()
    solver.load_problem(problem)
    solver.solve()
    self.assertEqual(value, solver.get_obj_value())
    for i in range(len(v)):
      self.assertEqual(solution[i], solver.get_col_solution()[i])
