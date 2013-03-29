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

"""Dummy solver."""

from les.solvers.solver import Solver
from les.problems.bilp_problem import BILPProblem

class DummySolver(Solver):
  """This class represents dummy solver, which solves BILPProblem derived
  problems.
  """

  def __init__(self):
    self._problem = None
    self._col_solution = None
    self._obj_value = None

  def get_problem(self):
    return self._problem

  def load_problem(self, problem):
    if not isinstance(problem, BILPProblem):
      raise TypeError()
    self._problem = problem

  def get_col_solution(self):
    return self._col_solution

  def get_obj_value(self):
    return self._obj_value

  def solve(self):
    self._col_solution = [1.] * self._problem.get_num_cols()
    if self._problem.check_col_solution(self._col_solution):
      self._obj_value = self._problem.get_obj_coefs().sum()
      return True
    self._col_solution = None
    return False
