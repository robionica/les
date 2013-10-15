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

from les import mp_model
from les.backend_solvers.knapsack_solver import knapsack_01_solver
from les.utils import unittest

class Knapsack01SolverTest(unittest.TestCase):

  def test_solve(self):
    knapsack = [0.0, 1.0, 1.0, 1.0]
    value = 21.0
    model = mp_model.build([8, 11, 6, 4],
                           [[5, 7, 4, 3]],
                           ['L'],
                           [14])
    solver = knapsack_01_solver.Knapsack01Solver()
    solver.load_model(model)
    solver.solve()
    solution = solver.get_solution()
    self.assert_equal(value, solution.get_objective_value())
    self.assert_equal(knapsack, solution.get_variables_values().tolist())

if __name__ == '__main__':
  unittest.main()
