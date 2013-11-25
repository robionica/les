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
from les.mp_model import mp_model_parameters
from les.mp_model import mp_submodel
from les.graphs import decomposition_tree

class MaxCliquesDecomposer(decomposer_base.DecomposerBase):

  def __init__(self, model):
    decomposer_base.DecomposerBase.__init__(self, model)
    model_params = mp_model_parameters.build(model)
    self._A = model_params.get_rows_coefficients()

  def _build_submodel(self, clique):
    rows_scope = set()
    cols_scope = list()
    for label in clique:
      var = self._model.get_variable_by_name(label)
      i = var.get_index()
      cols_scope.append(i)
      rows_indices = set(self._A.getcol(i).nonzero()[0])
      if not len(rows_scope):
        rows_scope.update(rows_indices)
      else:
        rows_scope = rows_scope.intersection(rows_indices)
    return mp_submodel.build(self._model, list(rows_scope), cols_scope)

  def decompose(self):
    self._decomposition_tree = decomposition_tree.DecompositionTree(self._model)
    igraph = interaction_graph.InteractionGraph(self.get_model())
    generator = networkx.find_cliques(igraph)
    # Root...
    prev_clique = generator.next()
    prev_submodel = self._build_submodel(prev_clique)
    self._decomposition_tree.add_node(prev_submodel)
    self._decomposition_tree.set_root(prev_submodel)
    # Build the rest of the tree...
    for clique in generator:
      submodel = self._build_submodel(clique)
      shared_cols_scope = set(clique) & set(prev_clique)
      self._decomposition_tree.add_node(submodel)
      self._decomposition_tree.add_edge(prev_submodel, submodel,
                                        shared_cols_scope)
      prev_clique, prev_submodel = clique, submodel
