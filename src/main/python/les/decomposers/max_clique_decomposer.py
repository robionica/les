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

import networkx

from les.graphs import interaction_graph
from les.decomposers import decomposer_base
from les.mp_model import MPModel
from les.mp_model import MPModelBuilder
from les.graphs import decomposition_tree
from les.utils import logging


class MaxCliqueDecomposer(decomposer_base.DecomposerBase):

  def __init__(self, model):
    decomposer_base.DecomposerBase.__init__(self, model)
    self._A = model.rows_coefficients

  def _build_submodel(self, clique):
    rows_scope = set()
    cols_scope = list()
    for label in clique:
      i = self._model.columns_names.index(label)
      cols_scope.append(i)
      rows_indices = set(self._A.getcol(i).nonzero()[0])
      if not len(rows_scope):
        rows_scope.update(rows_indices)
      else:
        rows_scope = rows_scope.intersection(rows_indices)
    return self._model.slice(list(rows_scope), cols_scope)

  def decompose(self):
    self._decomposition_tree = decomposition_tree.DecompositionTree(self._model)
    igraph = interaction_graph.InteractionGraph(self.get_model())
    cliques = list(map(set, networkx.find_cliques(igraph)))
    logging.debug("%d clique(s) were found." % len(cliques))
    submodels_cache = []
    for i, clique in enumerate(cliques):
      submodel = self._build_submodel(clique)
      self._decomposition_tree.add_node(submodel)
      submodels_cache.append(submodel)
      for j, other_clique in enumerate(cliques[:i]):
        other_submodel = submodels_cache[j]
        shared_cols_scope = clique & other_clique
        if shared_cols_scope:
          self._decomposition_tree.add_edge(submodel, other_submodel,
                                            shared_cols_scope)
    self._decomposition_tree.set_root(submodels_cache[-1])
