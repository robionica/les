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

from les.solvers.bilp_solver import BILPSolver
from les.problems.knapsack_problem import KnapsackProblem

class KnapsackSolverBase(BILPSolver):

  def __init__(self):
    BILPSolver.__init__(self)
    self._problem = None

  def load_problem(self, problem, details={}):
    """Loads problem to be solved. Converts the problem if neccessary.

    Args:
       problem: A :class:`KnapsackProblem` derived problem
    """
    # Try to convert problem to KnapsackProblem if required. Raises TypeError.
    if not isinstance(problem, KnapsackProblem):
      problem = KnapsackProblem(problem)
    self._problem = problem

class Knapsack01Solver(KnapsackSolverBase):
  """A dynamic programming algorithm for the 0-1 knapsack problem."""

  def __init__(self):
    KnapsackSolverBase.__init__(self)

  def solve(self):
    W = self._problem.get_max_weight()
    n = self._problem.get_num_items() - 1
    v = self._problem.get_values()
    w = self._problem.get_weights()
    c = []                 # create an empty 2D array
    for i in xrange(n + 1): # c[i][j] = value of the optimal solution using
      temp = [0] * (W + 1) # items 1 through i and maximum weight j
      c.append(temp)
    for i in xrange(1, n + 1):
      for j in xrange(1, W + 1):
        if w[i] <= j: # if item i will fit within weight j
          # add item i if value is better
          if v[i] + c[i - 1][j - w[i]] > c[i - 1][j]:
            c[i][j] = v[i] + c[i - 1][j - w[i]] # than without item i
          else:
            c[i][j] = c[i - 1][j] # otherwise, don't add item i
        else:
          c[i][j] = c[i - 1][j]
    self._obj_value = float(c[n][W]) # final value is in c[n][W]
    # Build col solution
    i = len(c) - 1
    W =  len(c[0])-1
    # set everything to not marked
    self._col_solution = [0.0] * (i + 1)
    while (i >= 0 and W >=0):
      if (i == 0 and c[i][W] >0 )or c[i][W] != c[i-1][W]:
        self._col_solution[i] = 1.0
        W = W - w[i]
      i = i-1

  def get_obj_value(self):
    return self._obj_value

  def get_col_solution(self):
    return self._col_solution

class FractionalKnapsackSolver(KnapsackSolverBase):
  """A greedy algorithm for the fractional knapsack problem."""

  def __init__(self):
    KnapsackSolverBase.__init__(self)

  def solve(self):
    n = self._problem.get_num_items()
    v = self._problem.get_values()
    w = self._problem.get_weights()
    # Sort in descending order
    order = sorted(range(n), key=lambda i: float(v[i]) / w[i], reverse=True);
    weight = 0.0 # current weight of the solution
    value = 0.0 # current value of the solution
    index = 0 # order[index] is the index in v and w of the item we're considering
    W = self._problem.get_max_weight()
    knapsack = [0.0] * n
    while (weight < W) and (index < n):
      # if we can fit the entire order[index]-th item
      if weight + w[order[index]] <= W:
        # ... add it and update weight and value
        knapsack[order[index]] = 1.0
        weight = weight + w[order[index]]
        value = value + v[order[index]]
      else:
        # ... otherwise, calculate the fraction we can fit ...
        fraction = (W - weight) / w[order[index]]
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
