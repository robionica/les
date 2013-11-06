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
from les.frontend_solver import shared_variables_enumerator

class _LazyDecompositionTreeTraversal:

  def __init__(self, tree):
    if not isinstance(tree, decomposition_tree.DecompositionTree):
      raise TypeError()
    if not tree.get_leaves():
      raise Error('Empty tree, no leaves.')
    self._tree = tree
    self._visited_nodes = set()
    self._unvisited_nodes = set(tree.get_leaves())

  def mark_node_as_visited(self, node):
    unvisited_parent_nodes = set()
    self._visited_nodes.add(node.get_name())
    self._unvisited_nodes.remove(node.get_name())
    for v in self._tree.predecessors(node.get_name()):
      if (v not in self._visited_nodes and
          set(self._tree.neighbors(v)) <= self._visited_nodes):
        unvisited_parent_nodes.add(v)
    self._unvisited_nodes.update(unvisited_parent_nodes)
    return [self._tree.node[name] for name in unvisited_parent_nodes]

  def get_unvisited_nodes(self):
    return [self._tree.node[name] for name in self._unvisited_nodes]


class SearchTree(object):

  def __init__(self, decomposition_tree):
    self._dtree_traversal = _LazyDecompositionTreeTraversal(decomposition_tree)
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
    candidate_model_params, partial_solution = enumerator.next()
    self._unsolved_models_counter[node] += 1
    self._unsolved_models[candidate_model_params.get_name()] = node
    if enumerator.has_next():
      self._enumerators[node] = enumerator
    return node.get_model(), candidate_model_params, partial_solution

  def mark_model_as_solved(self, model_params):
    node = self._unsolved_models.pop(model_params.get_name())
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
