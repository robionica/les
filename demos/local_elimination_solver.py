#!/usr/bin/env python
#
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

import time
import numpy as np

from les.problems import BILPProblem
from les.solvers import LocalEliminationSolver
from les.decomposers import FinkelsteinQBDecomposer
from les.data_models import SQLiteDataModel

# Build the problem
start = time.clock()
cons_matrix = np.matrix([[2., 3., 4., 1., 0., 0., 0., 0., 0.],
                         [1., 2., 3., 2., 0., 0., 0., 0., 0.],
                         [0., 0., 1., 4., 3., 4., 2., 0., 0.],
                         [0., 0., 2., 1., 1., 2., 5., 0., 0.],
                         [0., 0., 0., 0., 0., 0., 2., 1., 2.],
                         [0., 0., 0., 0., 0., 0., 3., 4., 1.]])
problem = BILPProblem([8, 2, 5, 5, 8, 3, 9, 7, 6],
                      True,
                      cons_matrix,
                      None,
                      [7, 6, 9, 7, 3, 5])
end = time.clock()
print "Build time: %6.4f second(s)" % (end - start)
# Decompose the problem
start = time.clock()
decomposer = FinkelsteinQBDecomposer()
decomposer.decompose(problem)
end = time.clock()
print "Decomposition time: %6.4f second(s)" % (end - start)
# Solving...
start = time.clock()
solver = LocalEliminationSolver(data_model=SQLiteDataModel())
solver.load_problem(problem, decomposer.get_decomposition_tree())
solver.solve()
end = time.clock()
print "Solving time: %6.4f second(s)" % (end - start)
print "Ojective value:", solver.get_obj_value()
