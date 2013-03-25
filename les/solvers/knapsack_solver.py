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

from les.solvers.milp_solver import MILPSolver
from les.problems.knapsack_problem import KnapsackProblem

class FractionalKnapsackSolver(MILPSolver):
  """A greedy algorithm for the fractional knapsack problem."""

  def __init__(self):
    self._problem = None

  def solve(self):
    n = self._problem.get_num_cols()
    v = self._problem.get_obj_coefs()
    m = self._problem.get_cons_matrix()
    rows, cols = m.nonzero()
    # Sort in descending order
    order = sorted(cols, key=lambda i: float(v[i]) / m[0, i], reverse=True);
    weight = 0.0 # current weight of the solution
    value = 0.0 # current value of the solution
    index = 0 # order[index] is the index in v and w of the item we're considering
    W = self._problem.get_upper_bounds()[0]
    knapsack = [0.0] * n
    while (weight < W) and (index < n):
      # if we can fit the entire order[index]-th item
      if weight + m[0, order[index]] <= W:
        # ... add it and update weight and value
        knapsack[order[index]] = 1.0
        weight = weight + m[0, order[index]]
        value = value + v[order[index]]
      else:
        # ... otherwise, calculate the fraction we can fit ...
        fraction = (W - weight) / m[0, order[index]]
        # ... and add this fraction
        knapsack[order[index]] = fraction
        weight = W
        value = value + v[order[index]] * fraction
      index = index + 1
    self._obj_value = value
    self._col_solution = knapsack

  def get_col_solution(self):
    return self._col_solution

  def get_obj_value(self):
    return self._obj_value

  def load_problem(self, problem):
    if not isinstance(problem, KnapsackProblem):
      raise TypeError()
    self._problem = problem
