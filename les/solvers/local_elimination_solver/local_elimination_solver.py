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

"""LocalEliminationSolver represents the general class of local elimination
algorithms (LEA) for computing information, that have decomposition approach and
that allow to calculate some global information about a solution of the entire
problem using local computations.
"""

import networkx as nx
import logging

from les.problems.bilp_problem import BILPProblem
from les.solvers.bilp_solver import BILPSolver

from les.decomposition_tree import DecompositionTree
from les.solvers.local_elimination_solver.data_models.data_model import DataModel
from les.solvers.local_elimination_solver.data_models.sqlite_data_model import SQLiteDataModel
from les.solvers.local_elimination_solver.distributors.thread_distributor_factory import ThreadDistributorFactory
from les.solvers.local_elimination_solver.distributors.distributor_factory import DistributorFactory
from les.solvers.local_elimination_solver import local_solver

class Statistics(object):

  def __init__(self):
    self._stats = {
      'calls': {
        'relaxation_solvers': dict([(cls.__name__, 0) for cls in relaxation_solver_classes]),
        'master_solver': 0,
        }
    }

class LocalEliminationSolver(BILPSolver):
  """This class represents local elimination solver (LES), which implements
  local elimination algorithm (LEA). The solver solves discrete optimization
  problems (DOP) defined by DILP class.

  Set `distributor` to `None` to disable distributors. In this case solver will
  solve subproblems one by one. By default ThreadDistributor() instance will be
  used.
  """

  # Logger for this class
  logger = logging.getLogger()

  def __init__(self, master_solver_factory, relaxation_solver_classes=[],
               data_model=SQLiteDataModel(),
               distributor_factory=ThreadDistributorFactory()):
    BILPSolver.__init__(self)
    self._obj_value = 0.0
    self._distributor = None
    self._decomposition_tree = None
    if not isinstance(data_model, DataModel):
      raise TypeError()
    self._data_model = data_model
    self._local_solver_settings = local_solver.Settings(data_model,
                                                        master_solver_factory,
                                                        relaxation_solver_classes)
    if distributor_factory:
      if not isinstance(distributor_factory, DistributorFactory):
        raise TypeError("distributor_factory must be derived from"
                        " DistributorFactory")
      self._distributor = distributor_factory.build(self._local_solver_settings)

  def get_problem(self):
    """Returns the problem instance that has to be solved by this solver."""
    return self._problem

  def get_data_model(self):
    """Returns :class:`DataModel` based instance."""
    return self._data_model

  def solve(self):
    if not self.get_problem():
      raise Exception("Error, nothing to solve!")
    self.logger.info("Solving problem %s" % self._problem.get_name())
    # If we have only one subproblem, skip the process and solve it with pure
    # master solver
    if self._decomposition_tree.get_num_nodes() == 1:
      raise NotImplementedError()
    self._data_model.configure(self._decomposition_tree.get_subproblems())
    if self._distributor:
      for subproblem in self._decomposition_tree.get_subproblems():
        self._distributor.put(subproblem)
      self._distributor.run()
    else:
      for subproblem in self._decomposition_tree.get_subproblems():
        solver = local_solver.LocalSolver(self._local_solver_settings)
        solver.solve(subproblem)
    # Process subproblems in a depth-first-search pre-ordering starting from the
    # root
    for node in nx.dfs_preorder_nodes(self._decomposition_tree,
                                      self._decomposition_tree.get_root()):
      subproblem = self._decomposition_tree.node[node]["subproblem"]
      cols = subproblem.get_shared_cols() | subproblem.get_local_cols()
      shared_cols = subproblem.get_shared_cols()
      self._data_model.process(subproblem)
    self._obj_value = self._data_model.get_max_obj_value(subproblem.get_name())

  # NOTE: on this moment it's user responsibility to preprocess problem and
  # build decomposition tree.
  def load_problem(self, problem, decomposition_tree, max_num_shared_cols=10):
    """Loads problem and its decomposition model represented by decomposition
    tree.

    Process decomposition tree and merge nodes according to max_num_shared_cols
    value.
    """
    if not isinstance(problem, BILPProblem):
      raise TypeError()
    if not isinstance(decomposition_tree, DecompositionTree):
      raise TypeError("decomposition_tree must be derived from DecompositionTree")
    self._original_decomposition_tree = decomposition_tree
    self._decomposition_tree = decomposition_tree.copy()
    has_updates = True
    while has_updates:
      has_updates = False
      for node in self._decomposition_tree.get_nodes(data=True):
        # Instead of computing the total number of shared cols from edges we can
        # simply take this number directly from the problem
        subproblem = node[1].get("subproblem")
        if subproblem.get_num_shared_cols() <= max_num_shared_cols:
          continue
        edges = sorted(self._decomposition_tree.in_edges(node[0], data=True)
                     + self._decomposition_tree.out_edges(node[0], data=True),
                     key=lambda e: len(e[2].get("shared_cols")), reverse=True)
        self.logger.info("Merge subproblems %s and %s" % (edges[0][0], edges[0][1]))
        self._decomposition_tree.merge_nodes(edges[0][0], edges[0][1])
        has_updates = True
        break
    self._problem = problem

  def get_obj_value(self):
    """Returns objective function value."""
    return self._obj_value
