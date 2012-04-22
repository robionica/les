#!/usr/bin/env python

import metis

from les.decomposers.decomposer import Decomposer
from les.interaction_graph import InteractionGraph

class MetisPartGraphDecomposer(Decomposer):

  def __init__(self):
    Decomposer.__init__(self)

  def decompose(self, problem, n):
    g = InteractionGraph(problem)
    edgecuts, parts = metis.part_graph(g, n, recursive=False, objtype="cut",
                                       numbering=0, minconn=True, iptype="edge")
    groups = []
    for i in xrange(n):
      groups.append([])
    for i, j in enumerate(parts):
      groups[j].append(i)
    print parts
    print groups

if __name__ == "__main__":
  from les.problems.bilp_problem import BILPProblem
  import numpy
  cons_matrix = numpy.matrix([[2., 3., 4., 1., 0., 0., 0., 0., 0.],
                              [1., 2., 3., 2., 0., 0., 0., 0., 0.],
                              [0., 0., 1., 4., 3., 4., 2., 0., 0.],
                              [0., 0., 2., 1., 1., 2., 5., 0., 0.],
                              [0., 0., 0., 0., 0., 0., 2., 1., 2.],
                              [0., 0., 0., 0., 0., 0., 3., 4., 1.]])
  problem = BILPProblem([8, 2, 5, 5, 8, 3, 9, 7, 6],
                        cons_matrix,
                        [7, 6, 9, 7, 3, 5])
  d = MetisPartGraphDecomposer()
  d.decompose(problem, 3)
