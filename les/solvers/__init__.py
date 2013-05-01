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

import les.config
from les.solvers.local_elimination_solver import LocalEliminationSolver
from les.solvers.dummy_solver import DummySolver
from les.solvers.dummy_solver_factory import DummySolverFactory
from les.solvers.knapsack_solver import FractionalKnapsackSolver
from les.solvers.knapsack_solver_factory import FractionalKnapsackSolverFactory
if les.config.HAS_SYMPHONY_SUPPORT:
  from les.ext.coin.osi_sym_solver_interface import OsiSymSolverInterface
  from les.ext.coin.osi_clp_solver_interface import OsiClpSolverInterface
  from les.ext.coin.osi_sym_solver_interface_factory import OsiSymSolverInterfaceFactory
  from les.ext.coin.osi_clp_solver_interface_factory import OsiClpSolverInterfaceFactory
if les.config.HAS_GLPK_SUPPORT:
  from les.solvers.glp_solver import GLPSolver
  from les.solvers.glp_solver_factory import GLPSolverFactory
