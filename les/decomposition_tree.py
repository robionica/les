# -*- coding: utf-8; -*-
#
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

import logging
import networkx as nx

from les.problems.problem import Problem, Subproblem

class DecompositionTree(nx.DiGraph):

  # Logger for this class
  logger = logging.getLogger()

  def __init__(self, problem, root):
    nx.DiGraph.__init__(self)
    if not isinstance(problem, Problem):
      raise TypeError("problem must be derived from Problem")
    self._problem = problem
    self.add_node(root)
    self._root = root

  def __str__(self):
    return "%s[num_nodes=%d, num_edges=%d]" % (self.__class__.__name__,
                                               self.get_num_nodes(),
                                               self.get_num_edges())

  def get_num_nodes(self):
    return len(self.get_nodes())

  def get_num_edges(self):
    return len(self.get_edges())

  def get_root(self):
    return self._root.get_name()

  def merge_nodes(self, node1, node2):
    """Merges node1 and node2 to node1 and removes node2. Creates new
    subproblem.
    """
    subproblem = self.node[node1]["subproblem"] + self.node[node2]["subproblem"]
    self.add_node(subproblem)
    # Process node2 successors
    for edge in self.edges(node2, data=True):
      self.add_edge(subproblem, self.node[edge[1]]["subproblem"],
                    edge[2].get("shared_cols"))
    self.remove_node(node2)
    #self.remove_edge(node1, node2)
    #print node1, self.edges(node1)
    # Process node1 predecessors
    #for pn in self.predecessors(node1):
    #  print pn
    self.remove_node(node1)
    # Did we remove the root?
    if self.get_root() in (node1, node2):
      self._root = subproblem

  def copy(self):
    """Returns shallow copy."""
    tree = DecompositionTree(self._problem, self._root)
    tree.add_nodes_from(self.nodes(data=True))
    tree.add_edges_from(self.edges(data=True))
    return tree

  def get_num_nodes(self):
    return len(self.node)

  def add_node(self, node):
    if not isinstance(node, Problem):
      raise TypeError("node must be derived from Problem: %s" % node)
    name_format = self._problem.subproblem_name_format
    node.set_name(name_format % len(self))
    super(DecompositionTree, self).add_node(node.get_name(), subproblem=node)

  def remove_node(self, node):
    for other in self.predecessors(node):
      self.node[node]["subproblem"].remove_dependecy(self.node[other]["subproblem"])
    for other in self.successors(node):
      self.node[other]["subproblem"].remove_dependecy(self.node[node]["subproblem"])
    super(DecompositionTree, self).remove_node(node)

  def add_edge(self, node1, node2, shared_cols=[]):
    nx.DiGraph.add_edge(self, node1.get_name(), node2.get_name(),
                        shared_cols=shared_cols)
    node2.add_dependency(node1, shared_cols)

  def get_subproblems(self):
    return [self.node[n]["subproblem"] for n in self.nodes()]

DecompositionTree.get_edges = DecompositionTree.edges
DecompositionTree.get_nodes = DecompositionTree.nodes
