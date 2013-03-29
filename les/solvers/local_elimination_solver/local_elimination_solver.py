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
import numpy as np
import logging

from les.problems.bilp_problem import BILPProblem
from les.solvers.milp_solver import MILPSolver
from les.sparse_vector import SparseVector

from .data_models.data_model import DataModel
from .data_models.sqlite_data_model import SQLiteDataModel
from .distributors import ThreadDistributor
from .distributors.distributor import Distributor

logger = logging.getLogger()

class _RelaxedProblemGenerator(object):

  def __init__(self, subproblem):
    self._subproblem = subproblem
    cons_matrix = subproblem.get_cons_matrix()[:,list(subproblem.get_local_cols())]
    # Objective function
    obj = SparseVector((1, subproblem.get_num_cols()), dtype=np.float16)
    for i in subproblem.get_local_cols():
      obj[i] = subproblem.get_obj_coefs()[i]
    # Build gen problem
    self._genproblem = BILPProblem(obj, True, cons_matrix, [],
                                   subproblem.get_rows_upper_bounds().copy())

  def _gen_initial_solution(self, mask):
    solution = SparseVector((1, self._subproblem.get_num_cols()), dtype=np.float16)
    for c, i in enumerate(self._subproblem.get_shared_cols()):
      solution[i] = (mask >> c) & 1
    return solution

  def gen(self, mask):
    if not isinstance(mask, (int, long)):
      raise TypeError("mask: %s" % type(mask))
    solution = self._gen_initial_solution(mask)
    self._genproblem.set_rows_upper_bounds(self._subproblem.get_rows_upper_bounds().copy())
    m = self._subproblem.get_cons_matrix()
    for i in self._subproblem.get_shared_cols():
      for ii, ij in zip(*m[:,i].nonzero()):
        self._genproblem.set_row_upper_bound(ii, \
        self._genproblem.get_rows_upper_bounds()[ii] - (m[ii, i+ij] * solution[i+ij]))
        # TODO: check row sense
        if self._genproblem.get_rows_upper_bounds()[ii] < 0:
          return None, None
    return self._genproblem, solution

class LocalEliminationSolver(MILPSolver):
  """This class represents local elimination solver (LES), which implements
  local elimination algorithm (LEA). The solver solves discrete optimization
  problems (DOP) defined by DILP class.
  """

  def __init__(self, master_solver, relaxation_solvers=[],
               data_model=SQLiteDataModel(), distributor=ThreadDistributor()):
    MILPSolver.__init__(self)
    if not issubclass(master_solver, MILPSolver):
      raise TypeError("master_solver must be subclass of MILPSolver: %s"
                      % master_solver)
    self._master_solver = master_solver
    self._relaxation_solvers = []
    self._solutions = {}
    self._obj_value = 0.0
    self._data_model = None
    self._distributor = None
    if distributor:
      self.set_distributor(distributor)
    if relaxation_solvers:
      self.set_relaxation_solvers(relaxation_solvers)
    if data_model:
      self.set_data_model(data_model)

  def set_relaxation_solvers(self, solvers):
    if not isinstance(solvers, (list, tuple)):
      raise TypeError()
    for solver in solvers:
      if not issubclass(solver, MILPSolver):
        raise TypeError()
    self._relaxation_solvers = solvers

  def get_problem(self):
    return self._problem

  def set_data_model(self, data_model):
    if not isinstance(data_model, DataModel):
      raise TypeError()
    self._data_model = data_model

  def get_data_model(self):
    """Returns DataModel based instance."""
    return self._data_model

  def set_distributor(self, distributor):
    if not isinstance(distributor, Distributor):
      raise TypeError()
    self._distributor = distributor

  def solve(self, distributor=None):
    """By default ThreadDistributor() instance will be used. Set `distributor`
    to `None` to disable distributors.
    """
    logger.info("Solving problem %s" % self._problem.get_name())
    if not self.get_problem():
      raise Exception("Error, nothing to solve!")
    if distributor:
      self.set_destributor(distributor)
    # Solve subproblems if this wasn't done yet
    solutions_storage = {}
    if distributor:
      for subproblem in self._decomposition_tree.get_subproblems():
        distributor.put(subproblem)
      distributor.run(self._solve_subproblem)
    else:
      for subproblem in self._decomposition_tree.get_subproblems():
        self._solve_subproblem(subproblem, )
    # Initialize data-model
    self._data_model.init(self._decomposition_tree.get_subproblems())
    # Process subproblems in a depth-first-search pre-ordering starting
    for node in nx.dfs_preorder_nodes(self._decomposition_tree,
                                      self._decomposition_tree.get_root()):
      subproblem = self._decomposition_tree.node[node]["subproblem"]
      cols = subproblem.get_shared_cols() | subproblem.get_local_cols()
      shared_cols = subproblem.get_shared_cols()
      solutions = self._solutions[subproblem]
      for col_solution, obj_value in solutions:
        self._data_model.write_solution(subproblem, col_solution, obj_value)
    # Get result objective value
    self._obj_value = self._data_model.get_max_obj_value(subproblem.get_name())

  def _solve_subproblem(self, subproblem):
    logger.info("Solving %s" % subproblem)
    # register space for solutions
    self._solutions[subproblem] = []
    # TODO: len(shared_cols) < max separator size
    generator = _RelaxedProblemGenerator(subproblem)
    # TODO: this is maximization pattern, add minimization pattern
    for mask in range((1 << len(subproblem.get_shared_cols())) - 1, -1, -1):
      # Start to iterate over possible assigns for shared columns
      relaxed_problem, result_col_solution = generator.gen(mask)
      if relaxed_problem:
        col_solution, obj_value = self._solve_relaxed_problem(relaxed_problem)
        for c, i in enumerate(subproblem.get_local_cols()):
          result_col_solution[i] = col_solution[c]
        for dep_subproblem, dep_cols in subproblem.get_dependencies().items():
          obj_value += sum([self._problem.get_obj_coefs()[i] * result_col_solution[i] for i in dep_cols])
        # Registers solution for a given subproblem.
        self._solutions[subproblem].append((result_col_solution, obj_value))

  def _solve_relaxed_problem(self, problem):
    for solver_class in self._relaxation_solvers:
      solver = solver_class()
      solver.load_problem(problem)
      solver.solve()
      if len(solver.get_col_solution()) \
            and not sum(solver.get_col_solution()) % 1.0 \
            and problem.check_col_solution(solver.get_col_solution()):
        return solver.get_col_solution(), solver.get_obj_value()
    # Use master solver
    solver = self._master_solver()
    solver.load_problem(problem)
    solver.solve()
    return solver.get_col_solution(), abs(solver.get_obj_value())

  def load_problem(self, problem, decomposition_tree):
    self._problem = problem
    self._decomposition_tree = decomposition_tree

  def get_obj_value(self):
    """Returns objective function value."""
    return self._obj_value
