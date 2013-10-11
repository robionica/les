#!/usr/bin/env python
#
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

from les import _pipeline
from les import backend_solvers
from les.executors import dummy_executor
from les.executors import executor_base
from les.mp_model import mp_model_parameters
from les.utils import unittest

DEFAULT_BACKEND_SOLVER_ID = backend_solvers.get_default_solver_id()

class _PipelineMock(_pipeline.Pipeline):

  def __init__(self):
    pass

class DummyExecutorTest(unittest.TestCase):

  def setup(self):
    self.pipeline = _PipelineMock()
    self.executor = dummy_executor.DummyExecutor(self.pipeline)

  def test_execute_task(self):
    params = mp_model_parameters.build(
      [8, 2, 5, 5, 8, 3, 9, 7, 6],
      [[2, 3, 4, 1, 0, 0, 0, 0, 0],
       [1, 2, 3, 2, 0, 0, 0, 0, 0],
       [0, 0, 1, 4, 3, 4, 2, 0, 0],
       [0, 0, 2, 1, 1, 2, 5, 0, 0],
       [0, 0, 0, 0, 0, 0, 2, 1, 2],
       [0, 0, 0, 0, 0, 0, 3, 4, 1]],
      ['<='] * 6,
      [7, 6, 9, 7, 3, 5]
    )
    task = executor_base.Task(params, DEFAULT_BACKEND_SOLVER_ID)
    result = self.executor.execute(task)
    self.assert_is_not_none(result)
    solution = result.get_solution()
    self.assert_is_not_none(solution)
    self.assert_equal(39.0, solution.get_objective_value())

if __name__ == '__main__':
  unittest.main()
