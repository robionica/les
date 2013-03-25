# -*- coding: utf-8; -*-

"""Given a collection of items G = {g_1, g_2,... , g_n}, where each item g_i =
<v_i, w_i> worths v_i dollars, and weights w_i kgs, we would like to fill a bag
with max-capacity of W kgs with items from G, so that the total value of items
in the bag is maximized.
"""

import numpy

from les.problems.milp_problem import MILPProblem

class KnapsackProblem(MILPProblem):
  """Constructor, where values is array of values, weights is array of weights,
  n is number of items in the bag, max_weight is maximum weight that we can
  carry in the bag.
  """

  def __init__(self, values, weights, max_weight):
    if not isinstance(values, (list, tuple)):
      raise TypeError()
    if not isinstance(weights, (list, tuple)):
      raise TypeError()
    if not isinstance(max_weight, (int, long)):
      raise TypeError()
    cons_matrix = numpy.matrix([weights])
    MILPProblem.__init__(self, values, cons_matrix=cons_matrix, cons_senses=[],
                         upper_bounds=[max_weight])
