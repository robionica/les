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

from les.mp_model import mp_model_parameters


class Error(Exception):
  pass


class Request(object):
  '''The request will be registered within a pipeline by the model name it
  contains. The request will be solved by the Executor that has to use solver
  with id `solver_id`.

  :param model_params: A
    :class:`~les.mp_model.mp_model_parameters.MPModelParameters` instance.
  '''

  def __init__(self, model=None):
    self._model = None
    self._id = None
    self._solver_id = None
    if model:
      self.set_model_parameters(model)

  def __str__(self):
    return ('%s[id="%s", solver_id=%s]' %
              (self.__class__.__name__, self.get_id(), self.get_solver_id()))

  def get_id(self):
    return self._id

  def get_model_parameters(self):
    '''Returns model parameters that will be used as the model to be solved by
    the solver.
    '''
    return self._model

  def get_solver_id(self):
    return self._solver_id

  def set_model(self, model_parameters):
    if not isinstance(model_parameters, mp_model_parameters.MPModelParameters):
      raise TypeError('model_params must be derived from MPModelParameters: ' +
                      str(type(model_parameters)))
    self._model = model_parameters
    self._id = model_parameters.get_name()

  def set_solver_id(self, solver_id):
    '''Set solved ID that has to be used in order to solve the model.

    :param solver_id: An `int` that represents solver identifier.
    '''
    self._solver_id = solver_id


class Response(object):

  def __init__(self, model_params, solution):
    self._model_params = model_params
    self._solution = solution

  def __str__(self):
    return '%s[id="%s"]' % (self.__class__.__name__, self.get_id())

  def get_id(self):
    return self._model_params.get_name()

  def get_solution(self):
    return self._solution


class ExecutorBase(object):
  '''This is base class for all executors. The executor executes requests generated
  by pipeline and monitors them in prodaction. Once the request has been performed
  the response will be sent back to the pipeline.
  '''

  def __init__(self):
    self._response_callback = lambda response: None

  @classmethod
  def build_response(self, *args, **kwargs):
    return Response(*args, **kwargs)

  @classmethod
  def build_request(self, *args, **kwargs):
    return Request(*args, **kwargs)

  def execute(self, request):
    raise NotImplementedError()

  def is_busy(self):
    return False

  def set_response_callback(self, callback):
    if not callable(callback):
      raise TypeError()
    self._response_callback = callback
