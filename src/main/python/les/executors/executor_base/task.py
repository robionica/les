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

class Task(object):

  def __init__(self, model_params, solver_id=None):
    if not isinstance(model_params, mp_model_parameters.MPModelParameters):
      raise TypeError('model_params must be derived from ModelParameters: ' +
                      str(type(model_params)))
    self._model_params = model_params
    self._solver_id = solver_id
    self._job_id = None
    self._id = id(self)

  def __str__(self):
    return '%s[id=%d, model_name="%s", solver_id=%s]' % \
        (self.__class__.__name__, self.get_id(), self._model_params.get_name(),
         self._solver_id)

  def get_id(self):
    return self._id

  def get_job_id(self):
    return self._job_id

  def set_job_id(self, id_):
    self._job_id = id_

  def set_solver_id(self, solver_id):
    self._solver_id = solver_id

  def get_solver_id(self):
    return self._solver_id

  def get_model_parameters(self):
    return self._model_params
