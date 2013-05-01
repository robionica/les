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

import itertools

from les.ext.coin import _osi_clp_solver_interface
from les.ext.coin import coin_utils
from les.solvers.bilp_solver_base import BILPSolverBase
from les.problems.problem import Problem

class OsiClpSolverInterface(_osi_clp_solver_interface.OsiClpSolverInterface,
                            BILPSolverBase):

  def __init__(self):
    BILPSolverBase.__init__(self)
    _osi_clp_solver_interface.OsiClpSolverInterface.__init__(self)
    self._problem = None

  def solve(self):
    self.initial_solve()

  def load_problem(self, problem, details={}):
    """Loads problem to the solver."""
    if not isinstance(problem, Problem):
      raise TypeError("Problem must be derived from Problem: %s" % type(problem))
    if not self._problem:
      details = {}
    # Setup objective functions
    if details.get("obj_coefs", True):
      for i, coef in enumerate(problem.get_obj_coefs()):
        (p, v) = coef
        col = coin_utils.CoinPackedVector()
        # NOTE: fix coef because of C++ signature
        self.add_col(col, 0., 1., float(v))
      # Set objective function sense
      self.set_obj_sense(-1)
    # Constraints
    if details.get("cons_matrix", True):
      for p, row in enumerate(problem.get_cons_matrix()):
        if not row.getnnz():
          continue
        r = coin_utils.CoinPackedVector();
        for i, v in itertools.izip(row.indices, row.data):
          r.insert(int(i), float(v))
        # NOTE: fix coef because of C++ signature
        self.add_row(r, "L", float(problem.get_rhs()[p]), 1.)
    elif details.get("rhs", True):
      pass
      for i in xrange(len(problem.get_rhs())):
        self.set_row_upper(i, float(problem.get_rhs()[i]))
    self._problem = problem
