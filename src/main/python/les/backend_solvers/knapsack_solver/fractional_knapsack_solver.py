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

from les.mp_model import mp_solution
from les.backend_solvers.knapsack_solver import knapsack_solver_base

class FractionalKnapsackSolver(knapsack_solver_base.KnapsackSolverBase):
  '''This class implements a greedy algorithm for the fractional knapsack
  problem model.
  '''

  def __init__(self):
    knapsack_solver_base.KnapsackSolverBase.__init__(self)
    self._solution = None

  def solve(self):
    '''Starts to solve knapsack problem model.'''
    n = self._model_params.get_num_items()
    v = self._model_params.get_profits()
    w = self._model_params.get_weights()
    # Sort in descending order
    order = sorted(range(n), key=lambda i: float(v[i]) / w[i], reverse=True);
    weight = 0.0  # current weight of the solution
    value = 0.0  # current value of the solution
    index = 0  # order[index] is the index in v and w of the considere item
    W = self._model_params.get_max_weight()
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
    self._solution = mp_solution.MPSolution()
    self._solution.set_status(mp_solution.MPSolution.OPTIMAL)
    self._solution.set_objective_value(value)
    self._solution.set_variables_values(self._model_params.get_columns_names(),
                                        knapsack)

  def get_solution(self):
    return self._solution
