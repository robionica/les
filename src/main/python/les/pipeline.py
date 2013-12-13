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

import Queue

from les import mp_model


class Request(object):
  """The request will be registered within a pipeline by the model name it
  contains. The request will be solved by the Executor that has to use solver
  with id `solver_id`.

  :param model: A :class:`~les.mp_model.mp_model.MPModel` instance.
  """

  def __init__(self, model=None):
    self._model = None
    self._id = None
    self._solver_id = None
    if model:
      self.set_model(model)

  def __str__(self):
    return ('%s[id="%s", solver_id=%s]' %
              (self.__class__.__name__, self.get_id(), self.get_solver_id()))

  def get_id(self):
    return self._id

  def get_model(self):
    """Returns model that has to be solved by the solver."""
    return self._model

  def get_solver_id(self):
    return self._solver_id

  def set_model(self, model):
    if not isinstance(model, mp_model.MPModel):
      raise TypeError("model must be derived from MPModel: " + str(type(model)))
    self._model = model
    self._id = model.get_name()

  def set_solver_id(self, solver_id):
    """Set solved ID that has to be used in order to solve the model.

    :param solver_id: An `int` that represents solver identifier.
    """
    self._solver_id = solver_id


class Response(object):

  def __init__(self, model, solution):
    self._model = model
    self._solution = solution

  def __str__(self):
    return "%s[id='%s']" % (self.__class__.__name__, self.get_id())

  def get_id(self):
    return self._model.get_name()

  def get_solution(self):
    return self._solution


class Pipeline(object):
  """This class implements pipeline that represents communication protocol
  between driver and executor. The driver produces requests that it stores in
  pipeline, then these requets will be executed by executor. Once the request
  has been executed, the response will be available for processing from the same
  pipeline.
  """

  def __init__(self):
    self._requests = Queue.Queue()
    self._responses = Queue.Queue()

  def has_responses(self):
    return not self._responses.empty()

  def build_response(self, *args, **kwargs):
    return Response(*args, **kwargs)

  def put_response(self, response):
    self._responses.put_nowait(response)

  def get_response(self, block=False, timeout=None):
    return self._responses.get(block, timeout)

  def has_requests(self):
    return not self._requests.empty()

  def build_request(self, *args, **kwargs):
    return Request(*args, **kwargs)

  def put_request(self, request):
    self._requests.put_nowait(request)

  def get_request(self, block=False, timeout=None):
    return self._requests.get(block, timeout)
