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

from les import object_base
from les.utils import logging
from les.utils import generator_base
from les.executors import executor_base
from les.graphs.decomposition_tree import DecompositionTree
from les.solution_tables import solution_table_base
from les import _generator

class _Job(object):

  def __init__(self, node):
    self._node = node
    self._generator = _generator.Generator(
      node.get_model(),
      shared_vars=tuple(node.get_shared_variables()),
      local_vars=tuple(node.get_local_variables())
    )

  def __str__(self):
    return '%s[model_name=%s]' \
        % (self.__class__.__name__,
           self._generator.get_model().get_name())

  def get_id(self):
    return self._generator.get_model().get_name()

  def get_node(self):
    return self._node

  def get_generator(self):
    return self._generator

  def get_model(self):
    return self._generator.get_model()

  def next_task(self):
    model_params, solution = self._generator.next()
    task = executor_base.Task(model_params)
    task.set_job_id(self.get_id())
    return task, solution

  def is_empty(self):
    return not self._generator.has_next()

class _PipelineIterator(generator_base.GeneratorBase):

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

  :param tree: A :class:`DecompositionTree` instance.
  :param solution_table: A
    :class:`les.solution_tables.solution_table.SolutionTableBase` instance.
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
    for leave in decomposition_tree.get_leaves():
      self._add_job(_Job(decomposition_tree.node[leave]))
    self.next_job()

  def __iter__(self):
    return _PipelineIterator(self)

  def _set_decomposition_tree(self, tree):
    if not isinstance(tree, DecompositionTree):
      raise TypeError()
    if not tree.get_leaves():
      raise Exception('Empty tree.')
    self._decomposition_tree = tree

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
    """Moves to the next job and returns it. The next job can be selected in
    case the currently active job exists and it is empty (no active tasks), and
    there is at least one pending job.
    """
    if self._active_job and not len(self._active_tasks):
      model = self._active_job.get_generator().get_model()
      for v in self._decomposition_tree.predecessors(model.get_name()):
        if (v not in self._jobs and
            set(self._decomposition_tree.neighbors(v)) <= set(self._jobs.keys())):
          self._add_job(_Job(self._decomposition_tree.node[v]))
    if len(self._waiting_job_ids):
      self._active_job = self._jobs[self._waiting_job_ids.popleft()]
      logging.debug('Next job is %s', self._active_job)
    else:
      self._active_job = None
    return self._active_job

  def next_task(self):
    """Returns next task that has to be executed."""
    if self._active_job.is_empty():
      self.next_job()
    if self.is_blocked() or self.is_empty():
      return None
    task, solution = self._active_job.next_task()
    task.set_solver_id(self._optimization_params.backend_solver)
    logging.debug('Next task is %s' % task)
    self._active_tasks[task.get_id()] = task
    self._solutions[task.get_id()] = solution
    return task

  def finalize_task(self, task):
    logging.debug('Finalize task %d', task.get_id())
    del self._active_tasks[task.get_id()]

  def process_result(self, result):
    if not isinstance(result, executor_base.Result):
      raise TypeError()
    try:
      task = self._active_tasks[result.get_task_id()]
    except KeyError, e:
      logging.warning("Task does't exist: %d" % result.get_task_id())
      return
    logging.debug('Process %s', result)
    # TODO(d2rk): move the following logic.
    job = self._jobs[task.get_job_id()]
    solution = self._solutions[task.get_id()]
    # TODO: fix abs()
    if result.get_solution().is_optimal():
      solution.set_objective_value(result.get_solution().get_objective_value())
      solution.update_variables_values(result.get_solution())
      self._solution_table.write_solution(job.get_model(), solution)
    self.finalize_task(task)

  def is_blocked(self):
    '''Returns whether pipeline is blocked.'''
    return (len(self._waiting_job_ids) and not self._active_job and
            len(self._active_tasks))

  def is_empty(self):
    '''Returns whether pipeline is empty.'''
    return not len(self._waiting_job_ids) and not self._active_job
