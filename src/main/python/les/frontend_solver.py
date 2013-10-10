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

from les import backend_solvers as backend_solver_manager
from les import mp_model
from les import _pipeline
from les import mp_solver_base
from les import frontend_solver_pb2
from les import executors as executor_manager
from les import decomposers as decomposer_manager
from les import solution_tables as solution_table_manager
from les.utils import logging

class Error(Exception):
  pass

class FrontendSolver(mp_solver_base.MPSolverBase):
  '''This class implements the optimization logic of local elimination
  solver.
  '''

  def __init__(self):
    self._model = None
    self._optimization_params = None

  @classmethod
  def _gen_optimization_parameters(self):
    params = frontend_solver_pb2.OptimizationParameters()
    default_backend_solver_id = backend_solver_manager.get_default_solver_id()
    if not default_backend_solver_id:
      raise Error('Cannot define default backend solver id.')
    params.backend_solver = default_backend_solver_id
    return params

  def _process_decomposition_tree(self, tree):
    # TODO(d2rk): merge nodes if necessary.
    for node in tree.get_nodes():
      if node.get_num_shared_variables() > self._optimization_params.max_num_shared_variables:
        logging.debug('node has too many shared variables: %d > %d',
                      node.get_num_shared_variables(),
                      params.max_num_shared_variables)
        return False
    return True

  def _solve_single_model(self):
    raise NotImplementedError()

  def get_model(self):
    '''Returns model solved by this solver.

    :returns: A :class:`~les.mp_model.mp_model.MPModel` instance.
    '''
    return self._model

  def load_model(self, model):
    if not isinstance(model, mp_model.MPModel):
      raise TypeError()
    if not model.is_binary():
      raise TypeError('Optimization can be applied only to binary integer '
                      'linear programming problems.')
    self._model = model

  def solve(self, params=None):
    if not self._model:
      raise Error()
    if params and not isinstance(params, frontend_solver_pb2.OptimizationParameters):
      raise TypeError()
    if not params:
      params = self._gen_optimization_parameters()
    self._optimization_params = params
    logging.info('Optimize model %s with %d rows and %d columns.',
                 self._model.get_name(), self._model.get_num_constraints(),
                 self._model.get_num_variables())
    solution_table = solution_table_manager.get_instance_of(params.solution_table)
    if not solution_table:
      logging.info('Cannot create solution table: %d', params.solution_table)
      return
    try:
      decomposer = decomposer_manager.get_instance_of(params.decomposer,
                                                      self._model)
      decomposer.decompose()
    except Exception, e:
      logging.exception('Decomposition has been failed.')
      return
    logging.info('Model has been successfully decomposed.')
    tree = decomposer.get_decomposition_tree()
    solution_table.set_decomposition_tree(tree)
    if not self._process_decomposition_tree(tree):
      return
    if tree.get_num_nodes() == 1:
      return self._solve_single_model()
    pipeline = _pipeline.Pipeline(params, decomposition_tree=tree,
                                  solution_table=solution_table)
    logging.info('Pipeline has been successfully created.')
    executor = executor_manager.get_instance_of(params.executor, pipeline)
    logging.debug('Executor: %s', executor.__class__.__name__)
    try:
      executor.run()
    except Exception, e:
      logging.exception('Executor failed.')
      return
    solution = solution_table.get_solution()
    # Apply solution.
    objective = self._model.get_objective()
    objective.set_value(solution.get_objective_value())
    # TODO(d2rk): set only triggered variables.
    for var in self._model.get_variables():
      if var.get_name() in solution.get_variables_names():
        var.set_value(solution.get_variable_value_by_name(var.get_name()))
