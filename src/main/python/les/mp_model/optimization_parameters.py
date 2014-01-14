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

from les import backend_solvers
from les.mp_model import mp_model_pb2
from les.executors import executors_pb2
from les.decomposers import decomposers_pb2
from les.drivers import drivers_pb2


class OptimizationParameters(object):

  def __init__(self):
    self._proto = mp_model_pb2.OptimizationParameters()
    self.driver.default_backend_solver = backend_solvers.get_default_solver_id()

  @property
  def driver(self):
    return self._proto.Extensions[drivers_pb2.driver_parameters]

  @property
  def executor(self):
    return self._proto.Extensions[executors_pb2.executor_parameters]

  @property
  def decomposer(self):
    return self._proto.Extensions[decomposers_pb2.decomposer_parameters]

  def get_protobuf(self):
    return self._proto

  @classmethod
  def build_from_protobuf(cls):
    raise NotImplementedError()
