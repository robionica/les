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

from les.mp_model import mp_model_builder
from les.backend_solvers.knapsack_solver import fractional_knapsack_solver
from les.utils import unittest


class FractionalKnapsackSolverTest(unittest.TestCase):

  def test_solve1(self):
    model = mp_model_builder.MPModelBuilder.build_from([8, 11, 6, 4],
                                                       [[5, 7, 4, 3]],
                                                       ['L'],
                                                       [14])
    solver = fractional_knapsack_solver.FractionalKnapsackSolver()
    solver.load_model(model)
    solver.solve()
    solution = solver.get_solution()
    self.assert_equal(22., solution.get_objective_value())
    self.assert_equal([1.0, 1.0, 0.5, 0.0],
                      solution.get_variables_values().tolist())

  def test_solve2(self):
    model = mp_model_builder.MPModelBuilder.build_from([50, 140, 60, 60],
                                                       [[5, 20, 10, 12]],
                                                       ['L'],
                                                       [30])
    solver = fractional_knapsack_solver.FractionalKnapsackSolver()
    solver.load_model(model)
    solver.solve()
    solution = solver.get_solution()
    self.assert_equal(220., solution.get_objective_value())
    self.assert_equal([1., 1., 0.5, 0.],
                      solution.get_variables_values().tolist())

  def test_solve_model_with_several_constraints(self):
    model = mp_model_builder.MPModelBuilder.build_from([8, 11, 6, 4],
                                                       [[1, 4, 2, 2],
                                                        [4, 3, 2, 1]],
                                                       ['L', 'L'],
                                                       [7, 7])
    solver = fractional_knapsack_solver.FractionalKnapsackSolver()
    solver.load_model(model)
    solver.solve()
    solution = solver.get_solution()
    self.assert_equal(22., solution.get_objective_value())
    self.assert_equal([1.0, 1.0, 0.5, 0.0],
                      solution.get_variables_values().tolist())


if __name__ == "__main__":
  unittest.main()
