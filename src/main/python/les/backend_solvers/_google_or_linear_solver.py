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
from les.mp_model import mp_model_parameters
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
    self._model_params = None

  def _set_solver(self, solver):
    if not isinstance(solver, pywraplp.Solver):
      raise TypeError
    self._solver = solver

  def load_model(self, model):
    '''Loads a given model to the solver.

    :param model: A :class:`les.mp_model.mp_model.MPModel` instance or
      :class:`les.mp_model.mp_model_parameters.MPModelParameters` instance.
    '''
    if not isinstance(model, mp_model.MPModel):
      raise TypeError()
    self._model = model
    self.load_model_params(mp_model_parameters.build(model))

  def load_model_params(self, params):
    if not isinstance(params, mp_model.MPModelParameters):
      raise TypeError()
    if not self._solver:
      raise Error()
    self._model_params = params
    # Build variables and objective functions
    self._vars = [None] * params.get_num_columns()
    for i in range(params.get_num_columns()):
      var = self._vars[i] = self._solver.BoolVar(params.get_column_name(i))
      self._solver.SetObjectiveCoefficient(var, params.get_objective_coefficient(i))
    # Build constraints
    if params.maximization():
      self._solver.SetMaximization()
    else:
      raise NotImplementedError()
    infinity = self._solver.Infinity()
    for i, row in enumerate(params.get_rows_coefficients()):
      if not row.getnnz():
        continue
      lb, ub = None, None
      if params.get_rows_senses()[i] == '>=':
        lb, ub = params.get_rows_rhs()[i], infinity
      elif params.get_rows_senses()[i] == '<=':
        lb, ub = -infinity, params.get_rows_rhs()[i]
      else:
        raise NotImplementedError()
      cons = self._solver.Constraint(lb, ub, params.get_row_name(i) or '')
      for j, v in itertools.izip(map(int, row.indices), map(float, row.data)):
        cons.SetCoefficient(self._vars[j], v)

  def get_solution(self):
    return self._solution

  def solve(self):
    if not self._model_params:
      raise Error('Nothing to solve')
    result_status = self._solver.Solve()
    self._solution = mp_solution.MPSolution()
    self._solution.set_status(_RESULT_STATUS_MAP[result_status])
    if not result_status == pywraplp.Solver.OPTIMAL:
      return
    self._solution.set_objective_value(self._solver.ObjectiveValue())
    self._solution.set_variables_values(self._model_params.get_columns_names(),
                                   [var.SolutionValue() for var in self._vars])
