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

"""Given a collection of items :math:`G = {g_1, g_2,... , g_n}`, where each item
:math:`g_i = <v_i, w_i>` worths :math:`v_i` dollars, and weights :math:`w_i`
kgs, we would like to fill a bag with max-capacity of :math:`W` kgs with items
from :math:`G`, so that the total value of items in the bag is maximized.

The following code snippet shows a simple way to define knapsack problem::

  problem = KnapsackProblem("MY_PROBLEM", ([8, 11, 6, 4], [5, 7, 4, 3], 14))

However the :class:`KnapsackProblem` instance can be created by converting from
another model instance, e.g. :class:`~les.problems.bilp_problem.BILPProblem`, as
follows::

  bilp_problem = BILPProblem.build_from_scratch(
    [8, 2, 5, 5, 8, 3, 9, 7, 6],
    [[2., 3., 4., 1., 0., 0., 0., 0., 0.],
     [1., 2., 3., 2., 0., 0., 0., 0., 0.],
     [0., 0., 1., 4., 3., 4., 2., 0., 0.],
     [0., 0., 2., 1., 1., 2., 5., 0., 0.],
     [0., 0., 0., 0., 0., 0., 2., 1., 2.],
     [0., 0., 0., 0., 0., 0., 3., 4., 1.]],
    [7, 6, 9, 7, 3, 5])
  knapsack_problem = KnapsackProblem("MY_PROBLEM", bilp_problem)

"""

import numpy

from les.problems.problem_base import ProblemBase
from les.problems.bilp_problem import BILPProblem

class KnapsackProblem(ProblemBase):
  """This class represents common knapsack problem model.

  :param optional name: A string that represents problem name.
  :param optional model: A model from each this problem instance has to be
    initialized. See :func:`read`.
  """

  def __init__(self, name=None, model=None):
    ProblemBase.__init__(self, name)
    self._weights = []
    self._values = []
    self._max_weight = 0
    self._original_problem = None # the parent problem if defined
    if model:
      self.read(model)

  def read_from_scratch(self, values, weights, max_weight):
    """Reads problem model from scratch.

    :param values: An array of values.
    :param weights: An array of weights.
    :param max_weight: Maximum weight that we can carry in the bag.
    """
    self._set_values(values)
    self._set_weights(weights)
    self._set_max_weight(max_weight)

  def read_from_bilpp(self, problem):
    """Reads and initializes this problem from the given BILP problem model.

    :param problem: A :class:`~les.problems.bilp_problem.BILPProblem` instance.
    :raises: TypeError
    """
    if not isinstance(problem, BILPProblem):
      raise TypeError
    # Sum all the constraints over the first one
    self._set_values(problem.get_objective().tocsr().data.tolist())
    self._set_weights(problem.get_lhs().sum(0).tolist()[0])
    self._set_max_weight(problem.get_rhs().sum())
    self._original_problem = problem

  def read(self, model):
    """Initializes this problem from the given model.

    :raises: TypeError

    .. seealso:: :func:`read_from_scratch`, :func:`read_from_bilpp`
    """
    if type(model) in (list, tuple) and len(model) == 3:
      self.read_from_scratch(model[0], model[1], model[2])
    elif type(model) in (BILPProblem,):
      self.read_from_bilpp(model)
    else:
      raise TypeError()

  def _set_values(self, values):
    if not isinstance(values, (list, tuple)):
      raise TypeError("values can be a list or tuple: %s" % type(values))
    self._values = values

  def _set_weights(self, weights):
    if not isinstance(weights, (list, tuple)):
      raise TypeError("weights can be a list or tuple")
    self._weights = weights

  def _set_max_weight(self, max_weight):
    if not isinstance(max_weight, (int, long, numpy.float32)):
      raise TypeError("max_weight can be an in or long: %s" % type(max_weight))
    self._max_weight = max_weight

  def get_values(self):
    """Returns a list of values."""
    return self._values

  def get_weights(self):
    """Returns a list of weights."""
    return self._weights

  def get_num_items(self):
    """Returns number of items in the bag."""
    return len(self._values)

  def get_max_weight(self):
    """Returns maximum weight that we can carry in the bag.

    :returns: An integer that represents max weight.
    """
    return self._max_weight
