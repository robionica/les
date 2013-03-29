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

from les.problems.bilp_problem import BILPProblem

class KnapsackProblem(BILPProblem):
  """Constructor, where values is array of values, weights is array of weights,
  n is number of items in the bag, max_weight is maximum weight that we can
  carry in the bag.
  """

  def __init__(self, values, weights, max_weight):
    if not isinstance(values, (list, tuple)):
      raise TypeError("values can be a list or tuple: %s" % type(values))
    if not isinstance(weights, (list, tuple)):
      raise TypeError("weights can be a list or tuple")
    if not isinstance(max_weight, (int, long, numpy.float32)):
      raise TypeError("max_weight can be an in or long: %s" % type(max_weight))
    cons_matrix = numpy.matrix([weights])
    BILPProblem.__init__(self, values, True, cons_matrix=cons_matrix,
                         rows_senses=[],
                         rows_upper_bounds=[max_weight])
    self._weights = weights
    self._values = values
    self._max_weight = max_weight

  @classmethod
  def build(cls, data):
    if isinstance(data, BILPProblem):
      # Sum all the constraints over the first one
      weights = data.get_cons_matrix().sum(0).tolist()[0]
      max_weight = data.get_rows_upper_bounds().sum()
      return cls(data.get_obj_coefs().values(), weights, max_weight)
    else:
      raise TypeError()

  def get_values(self):
    return self._values

  def get_weights(self):
    return self._weights

  def get_num_items(self):
    return len(self._values)

  def get_max_weight(self):
    """Returns maximum weight that we can carry in the bag."""
    return self._max_weight
