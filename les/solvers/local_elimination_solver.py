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
from scipy.sparse import csr_matrix, dok_matrix, hstack
import logging

from les.problems.problem import Problem
from les.solvers.symphony_proxy_solver import SymphonyProxySolver
from les.solvers.milp_solver import MILPSolver
from les.sparse_vector import SparseVector
from les.data_models.data_model import DataModel

logger = logging.getLogger()

class _RelaxedProblemGenerator(object):

  def __init__(self, subproblem):
    self._subproblem = subproblem
    # TODO: consider to use csc matrix instead of csr
    cons_matrix = hstack([subproblem.get_cons_matrix().getcol(i)
                          for i in subproblem.get_local_cols()], format="csr")

    # Objective function
    obj = SparseVector((1, subproblem.get_num_cols()), dtype=np.float16)
    for i in subproblem.get_local_cols():
      obj[i] = subproblem.get_obj_coefs()[i]
    # Build gen problem
    self._genproblem = Problem(obj, cons_matrix, [],
                               subproblem.get_upper_bounds().copy())

  def _gen_initial_solution(self, mask):
    solution = SparseVector((1, self._subproblem.get_num_cols()), dtype=np.float16)
    for c, i in enumerate(self._subproblem.get_shared_cols()):
      solution[i] = (mask >> c) & 1
    return solution

  def gen(self, mask):
    if not isinstance(mask, (int, long)):
      raise TypeError("mask: %s" % type(mask))
    solution = self._gen_initial_solution(mask)
    self._genproblem.set_upper_bounds(self._subproblem.get_upper_bounds().copy())
    m = self._subproblem.get_cons_matrix()
    for i in self._subproblem.get_shared_cols():
      col = m.getcol(i)
      for ii, ij in zip(*col.nonzero()):
        self._genproblem.set_upper_bound(ii, \
        self._genproblem.get_upper_bounds()[ii] - (m[ii, i+ij] * solution[i+ij]))
        # TODO: check row sense
        if self._genproblem.get_upper_bounds()[ii] < 0:
          return None, None
    return self._genproblem, solution

class LocalEliminationSolver(MILPSolver):

  def __init__(self, data_model=None):
    MILPSolver.__init__(self)
    self._solutions = {}
    self._obj_value = 0.0
    self._data_model = None
    if data_model:
      self.set_data_model(data_model)

  def get_problem(self):
    return self._problem

  def set_data_model(self, data_model):
    if not isinstance(data_model, DataModel):
      raise TypeError()
    self._data_model = data_model

  def get_data_model(self):
    return self._data_model

  def solve(self):
    if not self.get_problem():
      raise Exception("Error, nothing to solve!")
    # Solve subproblems if this wasn't done yet
    for subproblem in self._decomposition_tree.get_subproblems():
      self.solve_subproblem(subproblem)
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

  def solve_subproblem(self, subproblem):
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
        self._register_solution(subproblem, result_col_solution, obj_value)

  def _register_solution(self, subproblem, col_solution, obj_value):
    """Registers solution for a given subproblem."""
    self._solutions[subproblem].append((col_solution, obj_value))

  def _solve_relaxed_problem(self, problem):
    # 1. Solve with help of R0 relaxation - try to solve problem without
    #    constraints
    # Build max local solution
    col_solution = [1.] * problem.get_num_cols()
    if problem.check_col_solution(col_solution):
      return col_solution, problem.get_obj_coefs().sum()
    # TODO: add (2)
    # 3. Solve with help of R2 relaxation - use proxy solver
    solver = SymphonyProxySolver()
    solver.load_problem(problem)
    solver.solve()
    return solver.get_col_solution(), abs(solver.get_obj_value())

  def load_problem(self, problem, decomposition_tree):
    self._problem = problem
    self._decomposition_tree = decomposition_tree

  def get_obj_value(self):
    return self._obj_value
