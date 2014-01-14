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

from les import mp_model
from les.ext.google.operations_research.linear_solver import pywraplp
from les.backend_solvers import _google_or_linear_solver


class Error(Exception):
  pass


class SCIP(_google_or_linear_solver.GoogleORLinearSolver):
  """This class incapsulates SCIP solver represented by
  :class:`linear_solver.scip_interface.SCIPInterface`.
  """

  def load_model(self, model):
    if not isinstance(model, mp_model.MPModel):
      raise TypeError()
    solver = _google_or_linear_solver.pywraplp.Solver(
      model.get_name(),
      pywraplp.Solver.SCIP_MIXED_INTEGER_PROGRAMMING)
    self._set_solver(solver)
    _google_or_linear_solver.GoogleORLinearSolver.load_model(self, model)
