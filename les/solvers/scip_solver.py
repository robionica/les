#!/usr/bin/env python
#
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

import itertools
from zibopt import scip

from les.solvers.bilp_solver_base import BILPSolverBase

class SCIPSolver(BILPSolverBase):
  """This class incapsulates SCIP solver represented by
  :class:`zibopt.scip.solver`.
  """

  def __init__(self):
    BILPSolverBase.__init__(self)
    # scip.solver doesn't allow us to subclass it
    self._solver = scip.solver()
    self._objective = None
    self._solution = None
    self._cols = []

  def load_problem(self, problem):
    """Loads a given problem to the solver."""
    self._objective = None
    self._cols = [None] * problem.get_num_cols()
    for i, coef in enumerate(problem.get_obj_coefs()):
      (p, v) = coef
      self._cols[i] = self._solver.variable(vartype = scip.BINARY)
      if not self._objective:
        self._objective = float(v) * self._cols[i]
      else:
        self._objective += float(v) * self._cols[i]
    for p, row in enumerate(problem.get_cons_matrix()):
      if not row.getnnz():
        continue
      cons = float(row.data[0]) * self._cols[row.indices[0]]
      for c, v in itertools.izip(map(int, row.indices[1:]), map(float, row.data[1:])):
        cons += v * self._cols[c]
      self._solver += cons <= float(problem.get_rhs()[p])
    self._problem = problem

  def get_col_solution(self):
    return [self._solution[x] for x in self._cols]

  def get_obj_value(self):
    return self._solution.objective

  def solve(self):
    self._solution = self._solver.maximize(objective=self._objective)
