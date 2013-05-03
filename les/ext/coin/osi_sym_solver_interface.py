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

from les.ext.coin import _osi_sym_solver_interface
from les.ext.coin import coin_utils
from les.problems.problem_base import ProblemBase
from les.solvers.bilp_solver_base import BILPSolverBase

MINIMIZATION = +1
MAXIMIZATION = -1

class OsiSymSolverInterface(_osi_sym_solver_interface.OsiSymSolverInterface,
                            BILPSolverBase):
  """This class represents OSI Solver Interface for SYMPHONY."""

  def __init__(self):
    BILPSolverBase.__init__(self)
    _osi_sym_solver_interface.OsiSymSolverInterface.__init__(self)
    self._problem = None

  def solve(self):
    """"Invokes solver's built-in enumeration algorithm - branch and bound."""
    self.branch_and_bound()

  def load_problem(self, problem, details={}):
    """Loads problem to the solver.

    TODO: use OsiSymSolverInterface.loadProblem().
    """
    if not isinstance(problem, ProblemBase):
      raise TypeError("Problem must be derived from ProblemBase: %s" % type(problem))
    if not self._problem:
      details = {}
    # Setup objective functions
    if details.get("obj_coefs", True):
      # XXX: At some point we can not set column type when there is only one
      # column in the problem. Otherwise SYMPHONY crashes with segmentation
      # fault.
      if problem.get_num_cols() > 1:
        for i, coef in enumerate(problem.get_obj_coefs()):
          (p, v) = coef
          col = coin_utils.CoinPackedVector()
          # NOTE: fix coef because of C++ signature
          self.add_col(col, 0., 1., v.astype(float))
          # TODO: set column type
          self.set_integer(i)
      else:
        col = coin_utils.CoinPackedVector()
        self.add_col(col, 0., 1., problem.get_obj_coefs().values()[0].astype(float))
        self.set_integer(1)
      # Set objective function sense
      self.set_obj_sense(MAXIMIZATION)
    # Setup constraints
    if details.get("cons_matrix", True):
      for p, row in enumerate(problem.get_cons_matrix()):
        if not row.getnnz():
          continue
        r = coin_utils.CoinPackedVector();
        for i, v in itertools.izip(row.indices, row.data):
          r.insert(int(i), v.astype(float))
        # NOTE: fix coef because of C++ signature
        self.add_row(r, "L", float(problem.get_rhs()[p]), 1.)
    elif details.get("rhs", True):
      for i in xrange(len(problem.get_rhs())):
        self.set_row_upper(i, problem.get_rhs()[i].astype(float))
    self._problem = problem
