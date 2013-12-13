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
from les.executors import executor_base
from les.utils import logging


class Error(executor_base.Error):
  pass


class DummyExecutor(executor_base.ExecutorBase):
  """Dummy executor doesn't know how to parallelize solving process. It simply
  solves models one by one in order they come.
  """

  def execute(self, request):
    model = request.get_model()
    logging.debug('Solve model %s that has %d row(s) and %d column(s)'
                  ' with solver %s',
                  model.get_name(), model.get_num_rows(),
                  model.get_num_columns(), request.get_solver_id())
    solver = backend_solvers.get_instance_of(request.get_solver_id())
    if not solver:
      raise Error("Cannot instantiate backend solver by id: %d" %
                  request.get_solver_id())
    try:
      solver.load_model(model)
      solver.solve()
    except Error, e:
      # TODO: send back a report.
      logging.exception("Cannot execute given request: cannot solve the model.")
      return None
    response = self._pipeline.build_response(model, solver.get_solution())
    return response
