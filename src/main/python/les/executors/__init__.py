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

from les.executors import dummy_executor
from les.frontend_solver import frontend_solver_pb2

DUMMY_EXECUTOR_ID = frontend_solver_pb2.OptimizationParameters.DUMMY_EXECUTOR

_EXECUTORS_TABLE = {
  DUMMY_EXECUTOR_ID  : dummy_executor.DummyExecutor,
}

def get_instance_of(executor_id):
  '''Returns an instance of the executor defined by `executor_id`, or `None`
  otherwise.
  '''
  if not isinstance(executor_id, int):
    raise TypeError()
  if not executor_id in _EXECUTORS_TABLE:
    return None
  executor_class = _EXECUTORS_TABLE[executor_id]
  return executor_class()
