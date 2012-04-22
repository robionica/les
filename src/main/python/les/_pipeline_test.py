#!/usr/bin/env python
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

from les import _pipeline
from les import frontend_solver_pb2
from les.decomposers import finkelstein_qb_decomposer
from les import mp_model
from les import backend_solvers
from les.utils import unittest
from les.solution_tables import solution_table_base

class _SolutionTableMock(solution_table_base.SolutionTableBase):
  pass

class PipelineTest(unittest.TestCase):

  def test_num_relaxated_models(self):
    params = frontend_solver_pb2.OptimizationParameters()
    params.backend_solver = backend_solvers.SCIP_ID
    model = mp_model.build(
      [8, 2, 5, 5, 8, 3, 9, 7, 6],
      [[2, 3, 4, 1, 0, 0, 0, 0, 0],
       [1, 2, 3, 2, 0, 0, 0, 0, 0],
       [0, 0, 1, 4, 3, 4, 2, 0, 0],
       [0, 0, 2, 1, 1, 2, 5, 0, 0],
       [0, 0, 0, 0, 0, 0, 2, 1, 2],
       [0, 0, 0, 0, 0, 0, 3, 4, 1]],
      ['L'] * 6,
      [7, 6, 9, 7, 3, 5])
    decomposer = finkelstein_qb_decomposer.FinkelsteinQBDecomposer(model)
    decomposer.decompose()
    tree = decomposer.get_decomposition_tree()
    solution_table = _SolutionTableMock()
    pipeline = _pipeline.Pipeline(params, decomposition_tree=tree,
                                  solution_table=solution_table)
    counter = 0
    for task in pipeline:
      pipeline.finalize_task(task)
      counter += 1
    self.assert_equal(2 ** 2 + 2 ** 3 + 2, counter)

if __name__ == '__main__':
  unittest.main()
