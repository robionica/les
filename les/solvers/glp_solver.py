#!/usr/bin/env python
#
# -*- coding: utf-8; -*-
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

import glpk
import itertools

from les.solvers.bilp_solver_base import BILPSolverBase

class GLPSolver(glpk.LPX, BILPSolverBase):

  def __init__(self, *args, **kwargs):
    glpk.LPX.__init__(self, *args, **kwargs)
    BILPSolverBase.__init__(self)
    self._problem = None

  def load_problem(self, problem):
    self.obj.maximize = problem.maximize
    self.rows.add(problem.get_num_rows())
    self.cols.add(problem.get_num_cols())
    # Add objective function
    for i, coef in enumerate(problem.get_obj_coefs()):
      (p, v) = coef
      self.obj[i] = float(v)
      self.cols[i].bounds = 0., 1.
      self.cols[i].kind = bool
    # Add constraints
    for p, row in enumerate(problem.get_cons_matrix()):
      if not row.getnnz():
        continue
      self.rows[p].bounds = 0., problem.get_rhs()[p]
      self.rows[p].matrix = list(itertools.izip(map(int, row.indices),
                                                map(float, row.data)))
    self._problem = problem

  def get_problem(self):
    return self._problem

  def get_obj_value(self):
    return self.obj.value

  def get_col_solution(self):
    solution = []
    for i in range(self.get_problem().get_num_cols()):
      solution.append(self.cols[i].primal)
    return solution

  def solve(self):
    self.intopt()
