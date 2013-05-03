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

from les.problems.problem import Problem

class DecomposerBase(object):
  """Base class for a general decomposer. Decomposer provides decomposition
  technique, so that: each subproblem can be solved independently, the solution
  to the subproblems can be combined to solve the original problem.
  """

  def __init__(self):
    self._problem = None

  def get_problem(self):
    """Returns problem being decomposed by this decomposer."""
    return self._problem

  def _set_problem(self, problem):
    if not isinstance(problem, Problem):
      raise TypeError()
    self._problem = problem

  def decompose(self, problem):
    """Decomposes problem and build decomposition tree. See also
    :func:`get_decomposition_tree` method.
    """
    raise NotImplementedError()

  def get_decomposition_tree(self):
    """Returns result decomposition tree, once the problem has been
    decomposed.
    """
    raise NotImplementedError()
