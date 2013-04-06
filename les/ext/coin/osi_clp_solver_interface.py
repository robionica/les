#!/usr/bin/env python
#
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

from les.ext.coin import _osi_clp_solver_interface
from les.ext.coin import coin_utils
from les.solvers.bilp_solver import BILPSolver
from les.problems.problem import Problem

class OsiClpSolverInterface(_osi_clp_solver_interface.OsiClpSolverInterface,
                            BILPSolver):

  def __init__(self):
    BILPSolver.__init__(self)
    _osi_clp_solver_interface.OsiClpSolverInterface.__init__(self)
    self.set_log_level(0) # switch off printout

  def solve(self):
    self.initial_solve()

  def load_problem(self, problem):
    """Loads problem to the solver."""
    if not isinstance(problem, Problem):
      raise TypeError("Problem must be derived from Problem: %s" % type(problem))
    # Setup objective functions

    # XXX: At some point we can not set column type when there is only one
    # column in the problem. Otherwise SYMPHONY crashes with segmentation fault.

    for i, coef in enumerate(problem.get_obj_coefs()):
      (p, v) = coef
      col = coin_utils.CoinPackedVector()
      # NOTE: fix coef because of C++ signature
      self.add_col(col, 0., 1., float(v))
    # Constraints
    for p, row in enumerate(problem.get_cons_matrix()):
      if not row.getnnz():
        continue
      r = coin_utils.CoinPackedVector();
      for i, v in zip(row.indices, row.data):
        r.insert(int(i), float(v))
      # NOTE: fix coef because of C++ signature
      self.add_row(r, "L", float(problem.get_rows_upper_bounds()[p]), 1.)
    # Set objective function sense
    self.set_obj_sense(-1)
