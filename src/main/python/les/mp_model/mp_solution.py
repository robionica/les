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

'''Constains MP model solution or cadidate solution class (see
http://en.wikipedia.org/wiki/Candidate_solution).
'''

from __future__ import absolute_import

import collections
import numpy

from les.base import sparse_vector
from les.mp_model import mp_model_pb2

class MPSolution(object):
  '''This class represents model solution: objective value, variables
  values.
  '''

  OPTIMAL = mp_model_pb2.MPSolution.OPTIMAL
  FEASIBLE = mp_model_pb2.MPSolution.FEASIBLE
  INFEASIBLE = mp_model_pb2.MPSolution.INFEASIBLE
  NOT_SOLVED = mp_model_pb2.MPSolution.NOT_SOLVED

  def __init__(self):
    self._obj_value = None
    self._vars_names = None
    self._vars_values = None
    self._status = self.NOT_SOLVED

  def set_status(self, status):
    self._status = status

  def get_status(self):
    return self._status

  def is_optimal(self):
    return self._status == self.OPTIMAL

  def get_num_variables(self):
    if not self._vars_values is None:
      return self._vars_values.get_size()
    return 0

  def get_objective_value(self):
    return self._obj_value

  def get_variables_names(self):
    '''Returns a list of variables names.

    :returns: A list of strings.
    '''
    if not self._vars_names is None:
      return self._vars_names.keys()
    return []

  def get_variables_values(self):
    return self._vars_values

  def get_variable_value_by_name(self, name):
    i = self._vars_names[name]
    return self._vars_values[i]

  def set_objective_value(self, value):
    if not isinstance(value, float):
      raise TypeError('value has to be a float: %s' % type(value))
    self._obj_value = value

  def set_variable_value(self, name, value):
    i = self._vars_names[name]
    self._vars_values[i] = value

  def set_variables_values(self, names, values):
    if not isinstance(names, (list, tuple)):
      raise TypeError()
    if isinstance(values, (list, tuple, numpy.ndarray)):
      self._vars_values = sparse_vector.SparseVector(numpy.array(values))
    elif not isinstance(values, sparse_vector.SparseVector):
      raise TypeError()
    self._vars_names = collections.OrderedDict(
      zip(names, range(self.get_num_variables())))

  def update_variables_values(self, other):
    if not isinstance(other, MPSolution):
      raise TypeError()
    for i in other.get_variables_values().get_entries_indices():
      name = other.get_variables_names()[i]
      j = self._vars_names[name]
      self._vars_values[j] = other._vars_values[i]
