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

'''The interaction graph of the discrete optimization problem (DOP) is called an
undirected graph :math:`G=(X,E)`, such that:

1. Vertices :math:`X` of :math:`G` correspond to variables of the DOP;
2. Two vertices of :math:`G` are adjacent if corresponding variables interact.

Interaction graph of variables is also called constraint graph.
'''

import networkx

from les import mp_model
from les.mp_model import mp_model_parameters

def _extract_indices(m, i):
  start = m.indptr[i]
  size = m.indptr[i + 1] - start
  result = []
  for j in xrange(start, start + size):
    result.append(m.indices[j])
  return result

class InteractionGraph(networkx.Graph):
  '''This class represents an interaction graph of a given model.'''

  def __init__(self, model=None):
    networkx.Graph.__init__(self)
    self._model = None
    if model:
      self._read_model(model)

  def _read_model(self, model):
    if not isinstance(model, mp_model.MPModel):
      raise TypeError()
    # TODO: improve this
    model_params = mp_model_parameters.build(model)
    for p in xrange(model.get_num_constraints()):
      J = _extract_indices(model_params.get_rows_coefficients(), p)
      for i in xrange(0, len(J)):
        for j in xrange(i, len(J)):
          self.add_edge(model_params.get_columns_names()[J[i]],
                        model_params.get_columns_names()[J[j]])
    self._model = model

  def get_num_nodes(self):
    return len(self.nodes())

  def get_model(self):
    return self._model
