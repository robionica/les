#!/usr/bin/env python

import numpy
import unittest

from les.interaction_graph import InteractionGraph
from les.problems.milp_problem import MILPProblem

class InteractionGraphTest(unittest.TestCase):

  def test_constructor(self):
    cons_matrix = numpy.matrix([[2., 3., 4., 1., 0., 0., 0., 0., 0.],
                                [1., 2., 3., 2., 0., 0., 0., 0., 0.],
                                [0., 0., 1., 4., 3., 4., 2., 0., 0.],
                                [0., 0., 2., 1., 1., 2., 5., 0., 0.],
                                [0., 0., 0., 0., 0., 0., 2., 1., 2.],
                                [0., 0., 0., 0., 0., 0., 3., 4., 1.],
                                ])
    problem = MILPProblem([8, 2, 5, 5, 8, 3, 9, 7, 6],
                          True,
                          cons_matrix,
                          None,
                          [7, 6, 9, 7, 3, 5])
    g = InteractionGraph(problem)
    self.assertEqual(9, len(g.nodes()))
