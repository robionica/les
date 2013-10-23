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

'''This module contains variety of knapsack solvers: :class:`Knapsack01Solver`,
:class:`FractionalKnapsackSolver`.

The following code snippet shows a simple to define and solve knapsack problem::

  from les.solvers import FractionalKnapsackSolver
  from les.problems import KnapsackProblem

  problem = KnapsackProblem('PROBLEM', ([8, 11, 6, 4], [5,  7, 4, 3], 14))
  solver = FractionalKnapsackSolver()
  solver.load_problem(problem)
  solver.solve()
'''

import numpy

from les import mp_model
from les import mp_solver_base
from les.mp_model import mp_model_parameters

class _KnapsackModelParameters(object):

  def __init__(self):
    self._weights = []
    self._values = []
    self._max_weight = 0

  def set_values(self, values):
    if not isinstance(values, (list, tuple)):
      raise TypeError('values can be a list or tuple: %s' % type(values))
    self._values = values

  def set_weights(self, weights):
    if not isinstance(weights, (list, tuple)):
      raise TypeError('weights can be a list or tuple')
    self._weights = weights

  def set_max_weight(self, max_weight):
    if not isinstance(max_weight, (int, long, numpy.float32, numpy.float64)):
      raise TypeError('max_weight can be an int or long: %s' % type(max_weight))
    self._max_weight = max_weight

  def get_values(self):
    '''Returns a list of values.'''
    return self._values

  def get_weights(self):
    '''Returns a list of weights.'''
    return self._weights

  def get_num_items(self):
    '''Returns number of items in the bag.'''
    return len(self._values)

  def get_max_weight(self):
    '''Returns maximum weight that we can carry in the bag.

    :returns: An integer that represents max weight.
    '''
    return self._max_weight

class KnapsackSolverBase(mp_solver_base.MPSolverBase):
  '''Base solver class for knapsack derived solvers.'''

  def __init__(self):
    mp_solver_base.MPSolverBase.__init__(self)
    self._model = None
    self._model_params = None

  def load_model(self, model):
    '''Loads model to be solved.

    :param model: A :class:`~les.mp_model.mp_model.MPModel` instance.
    '''
    if not isinstance(model, mp_model.MPModel):
      raise TypeError()
    self.load_model_params(mp_model_parameters.build(model))
    self._model = model

  def load_model_params(self, params):
    if not isinstance(params, mp_model_parameters.MPModelParameters):
      raise TypeError()
    self._model_params = params
    self._kmodel_params = _KnapsackModelParameters()
    self._kmodel_params.set_values(params.get_objective_coefficients())
    # Sum all the constraints over the first one
    self._kmodel_params.set_weights(params.get_rows_coefficients().sum(0).tolist()[0])
    self._kmodel_params.set_max_weight(int(sum(params.get_rows_rhs())))
