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

"""The interaction graph of the discrete optimization problem (DOP) is called an
undirected graph G=(X,E), such that:

1. Vertices X of G correspond to variables of the DOP;
2. Two vertices of G are adjacent if corresponding variables interact.
"""

import networkx
import itertools

from les.problems.problem import Problem

def _extract_indices(m, i):
  start = m.indptr[i]
  size = m.indptr[i + 1] - start
  result = []
  for j in range(start, start + size):
    result.append(m.indices[j])
  return result

class InteractionGraph(networkx.Graph):
  """This class represents an interaction graph of a given problem."""

  def __init__(self, problem):
    networkx.Graph.__init__(self)
    self._problem = None
    self._set_problem(problem)
    m = problem.get_cons_matrix()
    # TODO: improve this
    for p in xrange(problem.get_num_rows()):
      J = _extract_indices(m, p)
      for i in range(0, len(J)):
        for j in range(i, len(J)):
          self.add_edge(J[i], J[j])

  def get_problem(self):
    return self._problem

  def _set_problem(self, problem):
    if not isinstance(problem, Problem):
      raise TypeError()
    self._problem = problem
