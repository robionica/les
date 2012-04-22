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

class SolutionTableBase(object):
  '''Base class for all solution models.'''

  def set_decomposition_tree(self, tree):
    raise NotImplementedError()

  def read_solution(self, model):
    '''Reads solution for a given model. Returns variables values and objective
    value.
    '''
    raise NotImplementedError()

  def write_solution(self, model, solution):
    '''Writes solution (variables values and objective value) for the given
    model to the data model.
    '''
    raise NotImplementedError()
