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

from les.solvers.bilp_solver import BILPSolver
from les.sparse_vector import SparseVector
from les.problems.bilp_problem import BILPProblem
from les.solvers.solver_factory import SolverFactory

class Settings(object):

  def __init__(self, data_model, master_solver_factory, relaxation_solver_factories):
    self._data_model = data_model
    if not isinstance(master_solver_factory, SolverFactory):
      raise TypeError("master_solver_factory must be derived from SolverFactory: %s"
                      % master_solver_factory)
    self._master_solver_factory = master_solver_factory
    if not isinstance(relaxation_solver_factories, (list, tuple)):
      raise TypeError()
    for factory in relaxation_solver_factories:
      if not isinstance(factory, SolverFactory):
        raise TypeError()
    self._relaxation_solver_factories = relaxation_solver_factories

  def get_data_model(self):
    return self._data_model

  def get_master_solver_factory(self):
    return self._master_solver_factory

  def get_relaxation_solver_factories(self):
    return self._relaxation_solver_factories

class _RelaxedProblemGenerator(object):

  def __init__(self, subproblem):
    self._subproblem = subproblem
    cons_matrix = subproblem.get_cons_matrix()[:,list(subproblem.get_local_cols())]
    # Objective function
    obj = SparseVector((1, subproblem.get_num_cols()), dtype=np.float16)
    for i in subproblem.get_local_cols():
      obj[i] = subproblem.get_obj_coefs()[i]
    # Build gen problem
    self._genproblem = BILPProblem(obj, cons_matrix, subproblem.get_rhs().copy())

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
      for ii, ij in zip(*m[:,i].nonzero()):
        self._genproblem.set_row_upper_bound(ii, \
            self._genproblem.get_rhs()[ii] - (m[ii, i+ij] * solution[i+ij]))
        if self._genproblem.get_rhs()[ii] < 0:
          return None, None
    return self._genproblem, solution

class LocalSolver(object):

  logger = logging.getLogger()

  def __init__(self, settings):
    self._data_model = settings.get_data_model()
    self._relaxation_solvers = settings.get_relaxation_solver_factories()
    self._master_solver_factory = settings.get_master_solver_factory()
    self._generator = None

  def solve(self, subproblem):
    self.logger.info("Solving %s..." % subproblem)
    self._generator = _RelaxedProblemGenerator(subproblem)
    # TODO: this is maximization pattern, add minimization pattern
    # NOTE: the first iteration is critial
    self._do_solve_iteration(subproblem, (1<<len(subproblem.get_shared_cols()))-1)
    # Start to iterate over all possible assigns for shared columns
    for mask in range((1 << len(subproblem.get_shared_cols())) - 2, -1, -1):
      self._do_solve_iteration(subproblem, mask)

  def _do_solve_iteration(self, subproblem, mask):
    relaxed_problem, result_col_solution = self._generator.gen(mask)
    if not relaxed_problem:
      return
    col_solution, obj_value = self._solve_relaxed_problem(relaxed_problem)
    for c, i in enumerate(subproblem.get_local_cols()):
      result_col_solution[i] = col_solution[c]
    for dep_subproblem, dep_cols in subproblem.get_dependencies().items():
      obj_value += sum([subproblem.get_obj_coefs()[i] * result_col_solution[i] for i in dep_cols])
    self._data_model.put(subproblem, result_col_solution, obj_value)

  def _solve_relaxed_problem(self, problem):
    for solver_factory in self._relaxation_solvers:
      solver = solver_factory.build()
      solver.load_problem(problem)
      solver.solve()
      s = sum(solver.get_col_solution())
      if s > 0 and not s % 1.0 \
            and problem.check_col_solution(solver.get_col_solution()):
        #self._stats['relaxation_solvers'][solver_class.__name__] += 1
        return solver.get_col_solution(), solver.get_obj_value()
    # Use master solver
    solver = self._master_solver_factory.build()
    solver.load_problem(problem)
    solver.solve()
    return solver.get_col_solution(), abs(solver.get_obj_value())
