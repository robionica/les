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

import numpy as np

from les.problems import MILPProblem
from les.solvers import LocalEliminationSolver
from les.decomposers import FinkelsteinQBDecomposer
from les.data_models import SQLiteDataModel

# Build the problem
cons_matrix = np.matrix([[2., 3., 4., 1., 0., 0., 0., 0., 0.],
                         [1., 2., 3., 2., 0., 0., 0., 0., 0.],
                         [0., 0., 1., 4., 3., 4., 2., 0., 0.],
                         [0., 0., 2., 1., 1., 2., 5., 0., 0.],
                         [0., 0., 0., 0., 0., 0., 2., 1., 2.],
                         [0., 0., 0., 0., 0., 0., 3., 4., 1.]])
problem = MILPProblem([8, 2, 5, 5, 8, 3, 9, 7, 6],
                      cons_matrix,
                      None,
                      [7, 6, 9, 7, 3, 5])
# Decompose the problem
decomposer = FinkelsteinQBDecomposer()
decomposer.decompose(problem)
# Initialize data model
data_model = SQLiteDataModel()
# Solving...
solver = LocalEliminationSolver(data_model=data_model)
solver.load_problem(problem, decomposer.get_decomposition_tree())
solver.solve()
