import metis

from les.decomposers.decomposer import Decomposer
from les.interaction_graph import InteractionGraph

class MetisPartGraphDecomposer(Decomposer):

  def __init__(self):
    Decomposer.__init__(self)

  def decompose(self, problem, n):
    g = InteractionGraph(problem)
    edgecuts, parts = metis.part_graph(g, n)
    groups = dict()
    for i, j in enumerate(parts):
      groups.setdefault(j, [])
      groups[j].append(i)
    print groups
