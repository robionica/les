# Copyright (c) 2013 Oleksandr Sviridenko
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


class Error(Exception):
  pass


class LazyDecompositionTreeTraversal:

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
