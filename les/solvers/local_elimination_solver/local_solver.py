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
import numpy as np
import itertools
from scipy import weave

from les.ext.scipy import sparse
from les.problems.bilp_problem import BILPProblem
from les.solvers.solver_factory import SolverFactory

class LocalSolverFactory(object):

  def __init__(self):
    self._data_model = None
    self._params = None

  def set_data_model(self, data_model):
    self._data_model = data_model

  def set_params(self, params):
    self._params = params

  def build(self):
    solver = LocalSolver(params=self._params)
    solver.set_data_model(self._data_model)
    return solver

class _Generator(object):
  """Relaxed problem generator."""

  def __init__(self, subproblem):
    self._subproblem = subproblem
    lhs = subproblem.get_lhs()[:,list(subproblem.get_local_variables())]
    # Objective function
    obj = sparse.dok_vector((1, subproblem.get_num_variables()), dtype=np.float16)
    for i in subproblem.get_local_variables():
      obj[i] = subproblem.get_objective()[i]
    # Build gen problem
    self._genproblem = BILPProblem.build_from_scratch(
      obj,
      lhs,
      [],
      subproblem.get_rhs().copy()
    )

  def gen(self, mask):
    if not type(mask) in (int, long):
      raise TypeError("mask: %s" % type(mask))
    solution = sparse.dok_vector((1, self._subproblem.get_num_variables()), dtype=np.float16)
    rhs = self._subproblem.get_rhs().copy()
    lhs = self._subproblem.get_lhs()
    for c, i in enumerate(self._subproblem.get_shared_variables()):
      solution[i] = (mask >> c) & 1
      for ii, ij in itertools.izip(*lhs[:,i].nonzero()):
        rhs[0, ii] -= lhs[ii, i] * solution[i]
        if rhs[0, ii] < 0:
          return None, None
    self._genproblem._set_rhs(rhs)
    return self._genproblem, solution

class LocalSolver(object):

  logger = logging.getLogger()

  def __init__(self, params={}):
    self._data_model = None
    self._generator = None
    self._params = params
    self._master_solver = None
    self._relaxation_solvers = []
    self._stats = {}

  def get_stats(self):
    return self._stats

  def set_data_model(self, data_model):
    self._data_model = data_model

  def get_data_model(self):
    return self._data_model

  def solve(self, problem):
    for factory in [self._params.master_solver_factory] \
          + self._params.relaxation_solver_factories:
      self._stats[factory.get_solver_class().__name__] = 0
    self.logger.info("Solving %s..." % problem)
    self._generator = _Generator(problem)
    self._record = 0.0
    # Initialize solvers
    self._master_solver = self._params.master_solver_factory.build()
    self._relaxation_solvers = []
    for solver_factory in self._params.relaxation_solver_factories:
      self._relaxation_solvers.append(solver_factory.build())
    # TODO: this is maximization pattern, add minimization pattern
    # Start to iterate over all possible assigns for shared columns
    map(lambda mask: self._do_solve_iteration(problem, mask),
        xrange((1 << len(problem.get_shared_variables())) - 1, -1, -1))

  def _do_solve_iteration(self, problem, mask):
    relaxed_problem, result_col_solution = self._generator.gen(mask)
    if not relaxed_problem:
      return
    col_solution, obj_value = self._solve_relaxed_problem(relaxed_problem)

    for c, i in enumerate(problem.get_local_variables()):
      result_col_solution[i] = col_solution[c]
    # Fix objective value
    for dep_problem, dep_cols in problem.get_dependencies().items():
      obj_value += np.sum([problem.get_objective()[i] * result_col_solution[i] for i in dep_cols])
    self._data_model.put(problem, result_col_solution, obj_value)

  def _solve_relaxed_problem(self, problem):
    for solver in self._relaxation_solvers:
      solver.load_problem(problem, {'obj_coefs': False, 'cons_matrix': False})
      solver.solve()
      s = np.sum(solver.get_col_solution())
      if s > 0 and not s % 1.0 \
            and problem.check_col_solution(solver.get_col_solution()):
        self._stats[solver.__class__.__name__] += 1
        return solver.get_col_solution(), solver.get_obj_value()
    # Use master solver
    self._master_solver.load_problem(problem, {'obj_coefs': False, 'cons_matrix': False})
    self._master_solver.solve()
    self._stats[self._master_solver.__class__.__name__] += 1
    # TODO: fix abs()
    return self._master_solver.get_col_solution(), abs(self._master_solver.get_obj_value())
