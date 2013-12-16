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

import timeit

from les import mp_model
from les.mp_model.optimization_parameters import OptimizationParameters
from les import pipeline
from les import drivers
from les import mp_solver_base
from les import executors as executor_manager
from les.utils import logging


class Error(Exception):
  pass


class FrontendSolver(mp_solver_base.MPSolverBase):
  """This class implements the optimization logic of local elimination
  solver.
  """

  def __init__(self):
    self._model = None
    self._optimization_params = None
    self._executor = None
    self._pipeline = None

  def get_model(self):
    '''Returns model solved by this solver.

    :returns: A :class:`~les.mp_model.mp_model.MPModel` instance.
    '''
    return self._model

  def load_model(self, model):
    if not isinstance(model, mp_model.MPModel):
      raise TypeError()
    self._model = model

  def solve(self, params=None):
    if not self._model:
      raise Error()
    if params and not isinstance(params, OptimizationParameters):
      raise TypeError()
    if not params:
      params = OptimizationParameters()
    self._optimization_params = params
    logging.info("Optimize model %s with %d rows and %d columns.",
                 self._model.get_name(), self._model.get_num_rows(),
                 self._model.get_num_columns())
    self._pipeline = pipeline.Pipeline()
    self._executor = executor_manager.get_instance_of(params.executor.executor,
                                                      self._pipeline)
    logging.info("Executor: %s", self._executor.__class__.__name__)
    try:
      self._driver = drivers.get_instance_of(params.driver.driver, self._model, params, self._pipeline)
    except Exception:
      logging.exception("Cannot create driver instance.")
      return
    logging.info("Driver: %s", self._driver.__class__.__name__)
    logging.info("Default backend solver is %d", params.driver.default_backend_solver)
    start_time = timeit.default_timer()
    try:
      self._executor.start()
      self._driver.start()
    except KeyboardInterrupt:
      self._executor.stop()
      self._driver.stop()
      return
    except Exception, e:
      logging.exception("Driver failed.")
      self._executor.stop()
      return
    self._executor.stop()
    logging.info("Model was solved in %f second(s)"
                 % (timeit.default_timer() - start_time,))
    self._model.set_solution(self._driver.get_solution())
