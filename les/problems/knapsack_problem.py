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
"""

import numpy

from les.problems.problem import Problem
from les.problems.bilp_problem import BILPProblem

class KnapsackProblem(Problem):
  """Constructor, where values is array of values, weights is array of weights,
  n is number of items in the bag, max_weight is maximum weight that we can
  carry in the bag.
  """

  def __init__(self, model=None):
    Problem.__init__(self)
    self._weights = []
    self._values = []
    self._max_weight = 0
    self._original_problem = None # the parent problem if defined
    if model:
      self.load_model(model)

  def load_model(self, model):
    if type(model) in (list, tuple) and len(model) == 3:
      self._set_values(model[0])
      self._set_weights(model[1])
      self._set_max_weight(model[2])
    elif isinstance(model, BILPProblem):
      # Sum all the constraints over the first one
      self._set_values(model.get_obj_coefs().tocsr().data.tolist())
      self._set_weights(model.get_cons_matrix().sum(0).tolist()[0])
      self._set_max_weight(model.get_rhs().sum())
      self._original_problem = model
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
    return self._values

  def get_weights(self):
    return self._weights

  def get_num_items(self):
    return len(self._values)

  def get_max_weight(self):
    """Returns maximum weight that we can carry in the bag."""
    return self._max_weight
