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

from les import mp_model
from les.mp_model import optimization_parameters
from les import backend_solvers
from les import executors
from les import drivers
from les import decomposers
from les.utils import logging
from les.cli.commands import command_base


DEFAULT_EXECUTOR = executors.DUMMY_EXECUTOR
DEFAULT_BACKEND_SOLVER_ID = backend_solvers.get_default_solver_id()
DEFAULT_DRIVER = drivers.LOCAL_ELIMINATION_DRIVER


class Optimize(command_base.CommandBase):

  default_arguments = (
    ("--executor", {
        "dest": "executor",
        "type": int,
        "metavar": "ID",
        "default": DEFAULT_EXECUTOR,
        "help": "executor id (default: %d)" % DEFAULT_EXECUTOR}),
    ("--driver", {
        "dest": "driver",
        "type": int,
        "metavar": "ID",
        "default": DEFAULT_DRIVER,
        "help": "driver name (default: %d)" % DEFAULT_DRIVER}),
    ("--default-backend-solver", {
        "dest": "default_backend_solver_id",
        "type": int,
        "metavar": "ID",
        "default": DEFAULT_BACKEND_SOLVER_ID,
        "help": ("default backend solver id (default: %d)"
                 % DEFAULT_BACKEND_SOLVER_ID)}),
  )

  def _get_optimization_parameters(self):
    params = optimization_parameters.OptimizationParameters()
    params.executor.executor = self._args.executor
    params.driver.default_backend_solver = self._args.default_backend_solver_id
    params.driver.driver = self._args.driver
    return params

  def run(self):
    model = mp_model.MPModelBuilder.build_from(self._args.file)
    params = self._get_optimization_parameters()
    model.optimize(params)
    file = sys.stdout
    file.write("Objective value: %f\n" % model.get_objective_value())
    file.write("Variables:\n")
    for i in range(model.get_num_columns()):
      file.write("%15s = %f\n" % (model.columns_names[i], model.columns_values[i]))
