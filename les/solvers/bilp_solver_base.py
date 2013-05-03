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

from les.solvers.solver_base import SolverBase

class BILPSolverBase(SolverBase):
  """Base solver class for 0-1 integer linear programming or binary integer
  linear programming problems represented by
  :class:`~les.problems.bilp_problem.BILPProblem` class.
  """

  def __init__(self):
    SolverBase.__init__(self)

  def get_col_solution(self):
    """Return primal solution.

    :returns: A list of primal variable values.
    """
    raise NotImplementedError()

  def get_obj_value(self):
    """Returns objective value.

    :returns: An objective function value.
    """
    raise NotImplementedError()
