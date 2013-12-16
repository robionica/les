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

'''This module contains variety of knapsack solvers: :class:`Knapsack01Solver`,
:class:`FractionalKnapsackSolver`.

The following code snippet shows a simple to define and solve knapsack problem::

  from les.solvers import FractionalKnapsackSolver
  from les.problems import KnapsackProblem

  problem = KnapsackProblem('PROBLEM', ([8, 11, 6, 4], [5,  7, 4, 3], 14))
  solver = FractionalKnapsackSolver()
  solver.load_problem(problem)
  solver.solve()
'''

import numpy

from les import mp_solver_base
from les.mp_model import mp_model
from les.mp_model import mp_model_builder
from les.mp_model.knapsack_model import KnapsackModel


class KnapsackSolverBase(mp_solver_base.MPSolverBase):
  '''Base solver class for knapsack derived solvers.'''

  def __init__(self):
    mp_solver_base.MPSolverBase.__init__(self)
    self._model = None

  def load_model(self, model):
    """Loads model to be solved.

    :param model: A :class:`~les.mp_model.mp_model.MPModel` instance.
    """
    if not isinstance(model, KnapsackModel):
      if isinstance(model, mp_model.MPModel):
        model = mp_model_builder.MPModelBuilder.build_knapsack_model(model)
      else:
        raise TypeError()
    else:
      raise TypeError()
    self._model = model
