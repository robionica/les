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
import time
import itertools

from les.sparse_vector import SparseVector
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
    cons_matrix = subproblem.get_cons_matrix()[:,list(subproblem.get_local_cols())]
    # Objective function
    obj = SparseVector((1, subproblem.get_num_cols()), dtype=np.float16)
    for i in subproblem.get_local_cols():
      obj[i] = subproblem.get_obj_coefs()[i]
    # Build gen problem
    self._genproblem = BILPProblem.build_from_scratch(obj, cons_matrix,
                                                      subproblem.get_rhs().copy())

  def _gen_initial_solution(self, mask):
    solution = SparseVector((1, self._subproblem.get_num_cols()), dtype=np.float16)
    for c, i in enumerate(self._subproblem.get_shared_cols()):
      solution[i] = (mask >> c) & 1
    return solution

  def gen(self, mask):
    if not isinstance(mask, (int, long)):
      raise TypeError("mask: %s" % type(mask))
    solution = self._gen_initial_solution(mask)
    self._genproblem.set_rhs(self._subproblem.get_rhs().copy())
    m = self._subproblem.get_cons_matrix()
    for i in self._subproblem.get_shared_cols():
      for ii, ij in itertools.izip(*m[:,i].nonzero()):
        self._genproblem.set_row_upper_bound(ii, \
            self._genproblem.get_rhs()[ii] - (m[ii, i+ij] * solution[i+ij]))
        if self._genproblem.get_rhs()[ii] < 0:
          return None, None
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
    # Initialize solvers
    self._master_solver = self._params.master_solver_factory.build()
    self._relaxation_solvers = []
    for solver_factory in self._params.relaxation_solver_factories:
      self._relaxation_solvers.append(solver_factory.build())
    # TODO: this is maximization pattern, add minimization pattern
    # Start to iterate over all possible assigns for shared columns
    map(lambda mask: self._do_solve_iteration(problem, mask),
        xrange((1 << len(problem.get_shared_cols())) - 1, -1, -1))

  def _do_solve_iteration(self, problem, mask):
    relaxed_problem, result_col_solution = self._generator.gen(mask)
    if not relaxed_problem:
      return
    col_solution, obj_value = self._solve_relaxed_problem(relaxed_problem)
    for c, i in enumerate(problem.get_local_cols()):
      result_col_solution[i] = col_solution[c]
    # Fix objective value
    for dep_problem, dep_cols in problem.get_dependencies().items():
      obj_value += sum([problem.get_obj_coefs()[i] * result_col_solution[i] for i in dep_cols])
    self._data_model.put(problem, result_col_solution, obj_value)

  def _solve_relaxed_problem(self, problem):
    for solver in self._relaxation_solvers:
      solver.load_problem(problem, {'obj_coefs': False, 'cons_matrix': False})
      solver.solve()
      s = sum(solver.get_col_solution())
      if s > 0 and not s % 1.0 \
            and problem.check_col_solution(solver.get_col_solution()):
        self._stats[solver.__class__.__name__] += 1
        return solver.get_col_solution(), solver.get_obj_value()
    # Use master solver
    self._master_solver.load_problem(problem,
                                     {'obj_coefs': False, 'cons_matrix': False})
    self._master_solver.solve()
    self._stats[self._master_solver.__class__.__name__] += 1
    # TODO: fix abs()
    return self._master_solver.get_col_solution(), abs(self._master_solver.get_obj_value())
