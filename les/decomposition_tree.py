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

import networkx as nx

from les.problems.problem import Problem, Subproblem

class DecompositionTree(nx.DiGraph):

  def __init__(self, problem, root):
    nx.DiGraph.__init__(self)
    if not isinstance(problem, Problem):
      raise TypeError()
    self._problem = problem
    self._root = id(root)
    self.add_node(root)

  def get_root(self):
    return self._root

  def add_node(self, p):
    if not isinstance(p, Subproblem):
      raise TypeError()
    name_format = self._problem.subproblem_name_format
    p._set_name(name_format % len(self))
    super(DecompositionTree, self).add_node(id(p), subproblem=p)

  def add_edge(self, sp1, sp2, shared_cols=[]):
    nx.DiGraph.add_edge(self, id(sp1), id(sp2))
    sp2.add_dependency(sp1, shared_cols)

  def get_subproblems(self):
    return [self.node[n]["subproblem"] for n in self.nodes()]
