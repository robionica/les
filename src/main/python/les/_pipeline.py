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

import collections

from les import generator
from les import object_base
from les.graphs import decomposition_tree as dtree
from les.mp_model import mp_model_parameters
from les.mp_model import mp_solution
from les.solution_tables import solution_table_base
from les.utils import logging
from les.utils import generator_base

class Error(Exception):
  pass

class Task(object):
  '''The task will be registered within a pipeline by the model name it
  contains. The task will be solved by the Executor that has to use solver with
  id `solver_id`.

  :param model_params: A
    :class:`~les.mp_model.mp_model_parameters.MPModelParameters` instance.
  '''

  def __init__(self, model_params):
    if not isinstance(model_params, mp_model_parameters.MPModelParameters):
      raise TypeError('model_params must be derived from MPModelParameters: ' +
                      str(type(model_params)))
    self._model_params = model_params
    self._id = model_params.get_name()
    self._solver_id = None
    self._job_id = None

  def __str__(self):
    return ('%s[id="%s", solver_id=%s]' %
              (self.__class__.__name__, self.get_id(), self.get_solver_id()))

  def get_id(self):
    return self._id

  def get_job_id(self):
    return self._job_id

  def set_job_id(self, job_id):
    self._job_id = job_id

  def get_model_parameters(self):
    '''Returns model parameters that will be used as the model to be solved by
    the solver.
    '''
    return self._model_params

  def set_solver_id(self, solver_id):
    '''Set solved ID that has to be used in order to solve the model.

    :param solver_id: An `int` that represents solver identifier.
    '''
    self._solver_id = solver_id

  def get_solver_id(self):
    return self._solver_id

class Result(object):

  def __init__(self, model_params, solution):
    self._model_params = model_params
    self._solution = solution

  def __str__(self):
    return '%s[id="%s"]' % (self.__class__.__name__, self.get_id())

  def get_id(self):
    return self._model_params.get_name()

  def get_solution(self):
    return self._solution

class Job(object):

  def __init__(self, optimization_params, node):
    self._optimization_params = optimization_params
    self._node = node
    self._generator = generator.Generator(
      node.get_model(),
      shared_vars=tuple(node.get_shared_variables()),
      local_vars=tuple(node.get_local_variables())
    )
    self._active_task_context = None
    self._id = self._generator.get_model().get_name()
    self._record = 0.0

  def __str__(self):
    return '%s[id="%s"]'  % (self.__class__.__name__, self._id)

  def get_id(self):
    return self._id

  def get_model(self):
    return self._generator.get_model()

  def get_record(self):
    '''Returns best objective function value found so far.'''
    return self._record

  def finalize(self):
    self._active_task_context = None

  def next_task(self):
    '''Returns next task from this job.'''
    if not self._active_task_context:
      model_params, solution_base = self._generator.next()
      task = Task(model_params)
      task.set_job_id(self.get_id())
      self._active_task_context = (task, list(self._optimization_params.relaxation_backend_solvers)
                                   + [self._optimization_params.default_backend_solver],
                                   solution_base)
    task, solver_ids, solution_base = self._active_task_context
    task.set_solver_id(solver_ids.pop(0))
    if not len(self._active_task_context[1]):
      self.finalize()
    return task, solution_base

  def is_empty(self):
    return not self._active_task_context and not self._generator.has_next()

  def set_record(self, record):
    if record < self._record:
      return False
    self._record = record
    return True

class PipelineIterator(generator_base.GeneratorBase):

  def __init__(self, pipeline):
    self._pipeline = pipeline

  def has_next(self):
    return not self._pipeline.is_empty()

  def next(self):
    '''Returns the next task that has to be executed or `None` if pipeline is
    blocked.
    '''
    task = self._pipeline.next_task()
    if not self.has_next() or task is None:
      raise StopIteration()
    return task

class Pipeline(object_base.ObjectBase):
  '''This class represents pipeline. The pipeline manages the order of solved
  models. It assigns a job for each new model (submodel) that has to be
  solved. Within a job a task will be assigned for each new relaxed model.

  :param tree: A :class:`~les.graphs.decomposition_tree.DecompositionTree`
    instance.
  :param solution_table: A
    :class:`les.solution_tables.solution_table_base.SolutionTableBase` instance.
  '''

  def __init__(self, optimization_parameters, decomposition_tree,
               solution_table):
    self._decomposition_tree = None
    self._optimization_params = optimization_parameters
    self._solution_table = None
    self._jobs = {}
    self._waiting_job_ids = collections.deque()
    self._active_job = None
    self._active_tasks = {}
    self._solutions = {}
    self._set_decomposition_tree(decomposition_tree)
    self._set_solution_table(solution_table)
    self.next_job()

  def __iter__(self):
    return PipelineIterator(self)

  def _set_decomposition_tree(self, tree):
    if not isinstance(tree, dtree.DecompositionTree):
      raise TypeError()
    if not tree.get_leaves():
      raise Error('Empty tree.')
    self._decomposition_tree = tree
    for leave in tree.get_leaves():
      self._add_job(Job(self._optimization_params, tree.node[leave]))

  def _set_solution_table(self, solution_table):
    if not isinstance(solution_table, solution_table_base.SolutionTableBase):
      raise TypeError('Unsupported data model type: %s' % type(solution_table))
    self._solution_table = solution_table

  def get_decomposition_tree(self):
    return self._decomposition_tree

  def get_solution_table(self):
    return self._solution_table

  def _add_job(self, job):
    # TODO(d2rk): check model type. Only BILP submodel can be registered
    # within a job.
    self._jobs[job.get_id()] = job
    self._waiting_job_ids.append(job.get_id())
    return job

  def next_job(self):
    '''Moves to the next job and returns it. The next job can be selected in
    case the currently active job exists and it is empty (no active tasks), and
    there is at least one pending job.
    '''
    if self._active_job and not len(self._active_tasks):
      model = self._active_job.get_model()
      for v in self._decomposition_tree.predecessors(model.get_name()):
        if (v not in self._jobs and
            set(self._decomposition_tree.neighbors(v)) <= set(self._jobs.keys())):
          self._add_job(Job(self._optimization_params,
                            self._decomposition_tree.node[v]))
    if len(self._waiting_job_ids):
      self._active_job = self._jobs[self._waiting_job_ids.popleft()]
      logging.debug('Next relaxed model is %s.', self._active_job.get_id())
    else:
      self._active_job = None
    return self._active_job

  def next_task(self):
    '''Returns next task that has to be executed by Executor.

    :returns: A :class:`Task` instance.
    '''
    if self._active_job.is_empty():
      self.next_job()
    if self.is_blocked() or self.is_empty():
      return None
    task, solution_base = self._active_job.next_task()
    self._active_tasks[task.get_id()] = task
    self._solutions[task.get_id()] = solution_base
    return task

  def finalize_task(self, task):
    del self._active_tasks[task.get_id()]

  def process_result(self, result):
    if not isinstance(result, Result):
      raise TypeError()
    try:
      task = self._active_tasks[result.get_id()]
    except KeyError, e:
      logging.warning("Task does't exist: %s" % result.get_id())
      return
    logging.debug('Process %s solution produced by %d.', result.get_id(),
                  task.get_solver_id())
    job = self._jobs[task.get_job_id()]
    solution = self._solutions.pop(task.get_id())
    # Check F3: whether optimal solution has been found.
    if (not result.get_solution().get_status() is mp_solution.MPSolution.NOT_SOLVED
        and not result.get_solution().get_variables_values() is None):
      if sum(result.get_solution().get_variables_values().tolist()) % 1.0:
        pass
      elif result.get_solution().is_optimal():
        # Check F2: do we need to continue?
        # NOTE: the record is associated with the current task.
        # NOTE: the objective value will be checked inside of set_record().
        if job.set_record(result.get_solution().get_objective_value()):
          logging.debug('Model %s has a new record: %f', result.get_id(),
                        result.get_solution().get_objective_value())
          solution.set_objective_value(result.get_solution().get_objective_value())
          solution.update_variables_values(result.get_solution())
          logging.debug('Write %s solution to the table.', result.get_id())
          self._solution_table.write_solution(job.get_model(), solution)
        job.finalize()
    self.finalize_task(task)

  def is_blocked(self):
    '''Returns whether pipeline is blocked.'''
    return (len(self._waiting_job_ids) and not self._active_job and
            len(self._active_tasks))

  def is_empty(self):
    '''Returns whether pipeline is empty.'''
    return not len(self._waiting_job_ids) and not self._active_job
