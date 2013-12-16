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

from les.graphs import decomposition_tree
from les.utils import logging
from les.drivers.local_elimination_driver import shared_variables_enumerator
from les.utils.lazy_decomposition_tree_traversal import LazyDecompositionTreeTraversal


class SearchTree(object):

  def __init__(self, decomposition_tree):
    self._dtree_traversal = LazyDecompositionTreeTraversal(decomposition_tree)
    self._enumerators = {}
    self._unsolved_models = {}
    self._unsolved_models_counter = {}
    for node in self._dtree_traversal.get_unvisited_nodes():
      self._add_node(node)

  def is_blocked(self):
    return not self.has_unresolved_nodes() and self.has_unsolved_models()

  def is_empty(self):
    return not self.has_unresolved_nodes() and not self.has_unsolved_models()

  def has_unsolved_models(self):
    return bool(len(self._unsolved_models))

  def has_unresolved_nodes(self):
    return bool(len(self._enumerators))

  def next_unsolved_model(self):
    node, enumerator = self._enumerators.popitem()
    candidate_model, partial_solution = enumerator.next()
    self._unsolved_models_counter[node] += 1
    self._unsolved_models[candidate_model.get_name()] = node
    if enumerator.has_next():
      self._enumerators[node] = enumerator
    return node.get_model(), candidate_model, partial_solution

  def mark_model_as_solved(self, model):
    node = self._unsolved_models.pop(model.get_name())
    self._unsolved_models_counter[node] -= 1
    if (not node in self._enumerators and
        self._unsolved_models_counter[node] == 0):
      self._remove_node(node)

  def _add_node(self, node):
    logging.debug('Add node %s', node.get_name())
    enumerator = shared_variables_enumerator.SharedVariablesEnumerator(
      node.get_model(), node.get_shared_variables(), node.get_local_variables())
    self._enumerators[node] = enumerator
    self._unsolved_models_counter[node] = 0

  def _remove_node(self, node):
    logging.debug('Remove node %s', node.get_name())
    nodes = self._dtree_traversal.mark_node_as_visited(node)
    for node in nodes:
      self._add_node(node)
