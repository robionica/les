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

class SolverBase(object):
  """Solvers base class.

  This class is the base of all solver classes.
  """

  def load_problem(self, problem):
    """Loads problem to the solver.

    :param problem: A :class:`Problem` instance.
    """
    raise NotImplementedError()

  def get_problem(self):
    """Returns problem solved by this solver.

    :returns: A :class:`Problem` instance.
    """
    raise NotImplementedError()

  def get_problem_type(self):
    """Returns the problem type."""
    problem = self.get_problem()
    return problem and type(problem) or None

  def solve(self):
    """Starts problem solving."""
    raise NotImplementedError()
