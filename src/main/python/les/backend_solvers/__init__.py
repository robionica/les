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

import sys

from les.utils import logging
from les.backend_solvers import backend_solvers_pb2

from les.backend_solvers.knapsack_solver import fractional_knapsack_solver
try:
  from les.backend_solvers import scip
except ImportError, e:
  logging.warning('SCIP is not supported: %s', e)

_SOLVERS_TABLE = {}

# Sync backend solvers IDs.
SCIP_ID = backend_solvers_pb2.SCIP
FRAKTIONAL_KNAPSACK_SOLVER_ID = getattr(backend_solvers_pb2,
                                        'FRAKTIONAL_KNAPSACK_SOLVER')

_DEFAULT_SOLVERS_TABLE = {}
if 'les.backend_solvers.scip' in sys.modules:
  _DEFAULT_SOLVERS_TABLE[SCIP_ID] = scip.SCIP
_SOLVERS_TABLE.update(_DEFAULT_SOLVERS_TABLE)

_RELAXATION_SOLVERS_TABLE = {
  FRAKTIONAL_KNAPSACK_SOLVER_ID: fractional_knapsack_solver.FractionalKnapsackSolver,
}
_SOLVERS_TABLE.update(_RELAXATION_SOLVERS_TABLE)

def get_default_solver_id():
  if len(_DEFAULT_SOLVERS_TABLE):
    return _DEFAULT_SOLVERS_TABLE.keys()[0]
  return None

def get_instance_of(solver_id, *args, **kwargs):
  '''Returns an instance of the solver defined by `solver_id`, or `None`
  otherwise.
  '''
  if not isinstance(solver_id, int):
    raise TypeError()
  if not solver_id in _SOLVERS_TABLE:
    return None
  solver_class = _SOLVERS_TABLE[solver_id]
  return solver_class(*args, **kwargs)
