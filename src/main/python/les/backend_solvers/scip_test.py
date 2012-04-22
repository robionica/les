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
from scipy import sparse

from les import mp_model
from les.backend_solvers import scip
from les.utils import unittest

SRC_DIR = os.path.join(os.path.dirname(__file__))

class SCIPTest(unittest.TestCase):

  def setup(self):
    self.solver = scip.SCIP()

  def test_solve1(self):
    model = mp_model.build(
      [8, 2, 5, 5, 8, 3, 9, 7, 6],
      [[2, 3, 4, 1, 0, 0, 0, 0, 0],
       [1, 2, 3, 2, 0, 0, 0, 0, 0],
       [0, 0, 1, 4, 3, 4, 2, 0, 0],
       [0, 0, 2, 1, 1, 2, 5, 0, 0],
       [0, 0, 0, 0, 0, 0, 2, 1, 2],
       [0, 0, 0, 0, 0, 0, 3, 4, 1]],
      ['L'] * 6,
      [7, 6, 9, 7, 3, 5])
    self.solver.load_model(model)
    self.solver.solve()
    solution = self.solver.get_solution()
    self.assert_equal(39.0, solution.get_objective_value())
    self.assert_equal([1.0, 0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0],
                      solution.get_variables_values().tolist())

  def test_solve2(self):
    test_filename = os.path.join(SRC_DIR, '..', 'mp_model',
                                 'mp_model_test_data', 'test2.mps')
    model = mp_model.build(test_filename)
    self.solver.load_model(model)
    self.solver.solve()
    values = [
      0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0,
      0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0,
      0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
      1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0,
      1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0,
      1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0,
      0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0,
      1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0
    ]
    solution = self.solver.get_solution()
    self.assert_equal(0.0, sum([var.get_value() for var in model.get_variables()]) % 1.0)
    self.assert_almost_equal(sum(values), sum(solution.get_variables_values().tolist()))
    self.assert_equal(3087.0, solution.get_objective_value())

  def test_solve3(self):
    model = mp_model.build(
      [42., 100., 22.],
      [[2., 3., 4.],
       [3., 4., 3.],
       [1., 3., 2.],
       [2., 1., 2.],
       [4., 3., 2.],
       [5., 4., 3.],
       [3., 2., 3.]],
      ['L'] * 7,
      [4., 5., 1., -1., 1., 4., 1.])
    self.solver.load_model(model)
    self.solver.solve()
    solution = self.solver.get_solution()
    self.assert_equal(None, solution.get_objective_value())

if __name__ == '__main__':
  unittest.main()
