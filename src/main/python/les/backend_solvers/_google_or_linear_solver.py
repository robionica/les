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

from les.ext.google.operations_research.linear_solver import pywraplp

from les import mp_model
from les.mp_model import mp_solution
from les import mp_solver_base


_RESULT_STATUS_MAP = {
  pywraplp.Solver.OPTIMAL    : mp_solution.MPSolution.OPTIMAL,
  pywraplp.Solver.FEASIBLE   : mp_solution.MPSolution.FEASIBLE,
  pywraplp.Solver.INFEASIBLE : mp_solution.MPSolution.INFEASIBLE,
  pywraplp.Solver.NOT_SOLVED : mp_solution.MPSolution.NOT_SOLVED,
}


class Error(Exception):
  pass


class GoogleORLinearSolver(mp_solver_base.MPSolverBase):

  def __init__(self):
    self._solver = None
    self._solution = None
    self._vars = []
    self._model = None

  def _set_solver(self, solver):
    if not isinstance(solver, pywraplp.Solver):
      raise TypeError
    self._solver = solver

  def load_model(self, model):
    '''Loads a given model to the solver.

    :param model: A :class:`les.mp_model.mp_model.MPModel` instance or
      :class:`les.mp_model.mp_model.MPModel` instance.
    '''
    if not isinstance(model, mp_model.MPModel):
      raise TypeError()
    if not self._solver:
      raise Error()
    self._model = model
    # Build variables and objective functions
    self._vars = [None] * model.get_num_columns()
    for i in range(model.get_num_columns()):
      var = self._vars[i] = self._solver.BoolVar(model.columns_names[i])
      self._solver.SetObjectiveCoefficient(var, model.objective_coefficients[i])
    # Build constraints
    if model.maximization():
      self._solver.SetMaximization()
    else:
      raise NotImplementedError()
    infinity = self._solver.Infinity()
    for i, row in enumerate(model.rows_coefficients):
      if not row.getnnz():
        continue
      lb, ub = None, None
      if model.rows_senses[i] == 'G':
        lb, ub = model.rows_rhs[i], infinity
      elif model.rows_senses[i] == 'L':
        lb, ub = -infinity, model.rows_rhs[i]
      else:
        raise ValueError("Unknown row sense: %s" % model.rows_senses[i])
      cons = self._solver.Constraint(lb, ub, model.rows_names[i] or '')
      for j, v in itertools.izip(map(int, row.indices), map(float, row.data)):
        cons.SetCoefficient(self._vars[j], v)

  def get_solution(self):
    return self._solution

  def solve(self):
    if not self._model:
      raise Error("Nothing to solve.")
    result_status = self._solver.Solve()
    self._solution = mp_solution.MPSolution()
    self._solution.set_status(_RESULT_STATUS_MAP[result_status])
    if not result_status == pywraplp.Solver.OPTIMAL:
      return
    self._solution.set_objective_value(self._solver.ObjectiveValue())
    self._solution.set_variables_values(self._model.columns_names,
                                   [var.SolutionValue() for var in self._vars])
