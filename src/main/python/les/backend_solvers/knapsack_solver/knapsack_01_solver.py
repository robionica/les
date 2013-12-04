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

from les.backend_solvers.knapsack_solver import knapsack_solver_base
from les.mp_model import mp_solution

class Knapsack01Solver(knapsack_solver_base.KnapsackSolverBase):
  '''This class implements a dynamic programming algorithm for the 0-1 knapsack
  problem.
  '''

  def __init__(self):
    knapsack_solver_base.KnapsackSolverBase.__init__(self)

  def solve(self):
    '''Starts to solve knapsack problem.'''
    W = int(self._model_params.get_max_weight())
    n = self._model_params.get_num_items() - 1
    v = self._model_params.get_profits()
    # TODO(d2rk): remove conversion.
    w = [int(_) for _ in self._model_params.get_weights()]
    c = []  # create an empty 2D array
    for i in xrange(n + 1):  # c[i][j] = value of the optimal solution using
      temp = [0] * (W + 1)  # items 1 through i and maximum weight j
      c.append(temp)
    for i in xrange(1, n + 1):
      for j in xrange(1, W + 1):
        if w[i] <= j:  # if item i will fit within weight j
          # add item i if value is better
          if v[i] + c[i - 1][j - w[i]] > c[i - 1][j]:
            c[i][j] = v[i] + c[i - 1][j - w[i]]  # than without item i
          else:
            c[i][j] = c[i - 1][j]  # otherwise, don't add item i
        else:
          c[i][j] = c[i - 1][j]
    self._solution = mp_solution.MPSolution()
    self._solution.set_objective_value(float(c[n][W]))
    # Set variables values.
    i = len(c) - 1
    W =  len(c[0])-1
    # Set everything as not marked
    vars_vals = [0.0] * (i + 1)
    while (i >= 0 and W >=0):
      if (i == 0 and c[i][W] >0 )or c[i][W] != c[i-1][W]:
        vars_vals[i] = 1.0
        W = W - w[i]
      i = i-1
    self._solution.set_variables_values(self._model_params.get_columns_names(),
                                        vars_vals)

  def get_solution(self):
    return self._solution
