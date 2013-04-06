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

class Distributor(object):
  """This is base class for all distributors, which allows local elimination
  solver to solve subproblems in parallel.
  """

  def __init__(self, local_solver_settings):
    self._local_solver_settings = local_solver_settings

  def get_local_solver_settings(self):
    return self._local_solver_settings

  def put(self, subproblem):
    raise NotImplementedError()

  def run(self):
    raise NotImplementedError()
