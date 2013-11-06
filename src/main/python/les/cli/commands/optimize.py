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

from __future__ import print_function

from les.frontend_solver import frontend_solver_pb2
from les import mp_model
from les import backend_solvers
from les import solution_tables
from les import executors
from les import decomposers
from les.utils import logging
from les.cli.commands import command_base

DEFAULT_SOLUTION_TABLE_ID = solution_tables.SQLITE_SOLUTION_TABLE_ID
DEFAULT_DECOMPOSER_ID = decomposers.FINKELSTEIN_QB_DECOMPOSER_ID
DEFAULT_EXECUTOR_ID = executors.DUMMY_EXECUTOR_ID
DEFAULT_BACKEND_SOLVER_ID = backend_solvers.get_default_solver_id()

class Optimize(command_base.CommandBase):
  default_arguments = (
    ('--decomposer', {
        'dest': 'decomposer_id',
        'type': int,
        'metavar': 'ID',
        'default': DEFAULT_DECOMPOSER_ID,
        'help': ('decomposer id (default: %d)' % DEFAULT_DECOMPOSER_ID)}),
    ('--solution-table', {
        'dest': 'solution_table_id',
        'type': int,
        'default': DEFAULT_SOLUTION_TABLE_ID,
        'metavar': 'ID',
        'help': 'solution table id (default: %d)' % DEFAULT_SOLUTION_TABLE_ID}),
    ('--executor', {
        'dest': 'executor_id',
        'type': int,
        'metavar': 'ID',
        'default': DEFAULT_EXECUTOR_ID,
        'help': 'executor id (default: %d)' % DEFAULT_EXECUTOR_ID}),
    ('--default-backend-solver', {
        'dest': 'default_backend_solver_id',
        'type': int,
        'metavar': 'ID',
        'default': DEFAULT_BACKEND_SOLVER_ID,
        'help': ('default backend solver id (default: %d)'
                 % DEFAULT_BACKEND_SOLVER_ID)}),
  )

  def run(self):
    model = mp_model.build(self._args.file)
    optimization_params = frontend_solver_pb2.OptimizationParameters()
    optimization_params.decomposer = self._args.decomposer_id
    optimization_params.executor = self._args.executor_id
    optimization_params.default_backend_solver = self._args.default_backend_solver_id
    model.optimize(optimization_params)
    print('Objective value:', model.get_objective_value())
    print('Variables:')
    for var in model.get_variables():
      print('%15s = %f' % (var.get_name(), var.get_value()))
