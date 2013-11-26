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

from __future__ import absolute_import

import numpy
from scipy import sparse

from les.utils import logging

class Error(Exception):
  pass

class MPModelParameters(object):
  '''This class represents model data that can be processed by the solvers.
  '''

  DEFAULT_NAME = 'UNKNOWN'
  NAME_FORMAT = 'P%d'
  VARIABLE_NAME_FORMAT = 'x{index}'
  CONSTRAINT_NAME_FORMAT = 'c{index}'

  def __init__(self, model=None):
    self._name = None
    self._maximization = True
    self._obj_coefs = []
    self._obj_name = None
    self._obj_offset = 0.0
    self._cols_lower_bounds = []
    self._cols_upper_bounds = []
    self._cols_names = []
    self._rows_names = []
    self._rows_coefs = None
    self._rows_rhs = []
    self._rows_senses = []
    if model:
      self.read_model(model)

  def __str__(self):
    return ('%s[num_rows=%d, num_columns=%d, maximization=%s]' %
            (self.__class__.__name__, self.get_num_rows(),
             self.get_num_columns(), self.maximization()))

  @classmethod
  def build(cls, *args, **kwargs):
    if not len(args) and not len(kwargs):
      return cls()
    elif len(args) == 1:
      return cls(args[0])
    else:
      return cls.build_from_scratch(*args, **kwargs)

  @classmethod
  def build_from_mps(cls):
    raise NotImplementedError()

  @classmethod
  def build_from_scratch(cls, objective_coefficients, rows_coefficients,
                         rows_senses, rows_rhs,
                         columns_lower_bounds=[], columns_upper_bounds=[],
                         columns_names=[]):
    params = cls()
    params.set_objective_from_scratch(objective_coefficients)
    params.set_columns_from_scratch(columns_lower_bounds, columns_upper_bounds,
                                    columns_names)
    params.set_rows_from_scratch(rows_coefficients, rows_senses, rows_rhs)
    return params

  def maximization(self):
    return self._maximization

  def minimization(self):
    return self._minimization

  def set_columns_from_scratch(self, columns_lower_bounds=[],
                               columns_upper_bounds=[], columns_names=[]):
    if columns_lower_bounds:
      self._cols_lower_bounds = columns_lower_bounds
    if columns_upper_bounds:
      self._cols_upper_bounds = columns_upper_bounds
    if columns_names:
      self._cols_names = columns_names

  def check_columns_values(self, columns_values):
    '''Checks whether the given columns values are correct.

    :param columns_values: A list of column values.

    :returns: ``True`` or ``False``.
    '''
    raise NotImplementedError()
    # TODO: solution can be a tuple, list or sparse.base.spmatrix
    if type(columns_values) in (tuple, list):
      columns_values = numpy.array(columns_values)
    if columns_values.shape[0] != self.get_num_columns():
      logging.warning("Number of columns values doesn't match number of "
                      "columns: %d != %d", columns_values.shape[0],
                      self.get_num_columns())
      return False
    v = self._rows_coefs.dot(columns_values)
    for i in xrange(len(v)):
      # TODO: add sense.
      if not v[i] <= self._rows_rhs[i]:
        return False
    return True

  def set_objective_from_scratch(self, coefficients):
    if isinstance(coefficients, tuple):
      self._obj_coefs = list(coefficients)
    if not isinstance(coefficients, list):
      raise TypeError('coefficients: %s' % coefficients)
    n = len(coefficients)
    self._cols_lower_bounds = [0.0] * n
    self._cols_upper_bounds = [1.0] * n
    self._cols_names = []
    for i in range(n):
      self._cols_names.append(self.VARIABLE_NAME_FORMAT.format(index=i))
    self._obj_coefs = coefficients

  def set_objective_offset(self, offset):
    self._obj_offset = offset

  def set_rows_from_scratch(self, coefficients, senses, rhs, names=[]):
    # Normalize matrix of coefficients
    if isinstance(coefficients, numpy.matrix):
      coefficients = sparse.csr_matrix(coefficients)
    elif isinstance(coefficients, list):
      coefficients = sparse.csr_matrix(numpy.matrix(coefficients))
    # Normalize RHS
    if isinstance(rhs, (tuple, list)):
      rhs = list(rhs)
    else:
      raise TypeError()
    # TODO(d2rk): Normalize senses.
    if (coefficients.shape[0] != len(senses) or
        len(senses) != len(rhs)):
      raise Exception()
    self._rows_coefs = coefficients
    self._rows_senses = senses
    self._rows_rhs = rhs

  def read_model(self, model):
    self.set_name(model.get_name())
    m = model.get_num_constraints()
    n = model.get_num_variables()
    objective = model.get_objective()
    if not objective:
      raise Error()
    # Process objective function
    self._obj_coefs = [0.0] * n
    self._cols_lower_bounds = [0.0] * n
    self._cols_upper_bounds = [1.0] * n
    self._cols_names = [None] * n
    for var in model.get_variables():
      self._obj_coefs[var.get_index()] = objective.get_coefficient(var)
      self._cols_lower_bounds[var.get_index()] = var.get_lower_bound()
      self._cols_upper_bounds[var.get_index()] = var.get_upper_bound()
      self._cols_names[var.get_index()] = var.get_name()
    self._obj_name = objective.get_name()
    # Process constraints coefficients, senses and right-hand side.
    cons_coefs = sparse.dok_matrix((m, n), dtype=float)
    self._rows_senses = []
    self._rows_rhs = [0.0] * m
    self._rows_names = [None] * m
    for constraint in model.get_constraints():
      i = constraint.get_index()
      for var in constraint.get_variables():
        cons_coefs[i, var.get_index()] = constraint.get_coefficient(var)
      self._rows_senses.append(constraint.get_sense())
      self._rows_rhs[i] = constraint.get_rhs()
      self._rows_names[i] = constraint.get_name()
    self._rows_coefs = cons_coefs.tocsr()

  def get_num_columns(self):
    return self._rows_coefs.shape[1]

  def get_columns_indices(self):
    return range(len(self._obj_coefs))

  def get_num_rows(self):
    return self._rows_coefs.shape[0]

  def get_objective_coefficients(self):
    return self._obj_coefs

  def get_objective_coefficient(self, i):
    return self._obj_coefs[i]

  def get_objective_name(self):
    return self._obj_name

  def get_objective_offset(self):
    return self._obj_offset

  def get_rows_coefficients(self):
    '''Returns matrix of constraints coefficients.

    :returns: A :class:`scipy.sparse.csr_matrix` instance. By default returns
      ``None``.
    '''
    return self._rows_coefs

  def get_rows_names(self):
    '''Returns list of rows names.'''
    return self._rows_names

  def get_row_name(self, i):
    return len(self._rows_names) and self._rows_names[i] or None

  def get_rows_rhs(self):
    '''Returns vector that represents right-hand side.'''
    return self._rows_rhs

  def get_rows_senses(self):
    return self._rows_senses

  def get_column_lower_bound(self, i):
    if not isinstance(i, int):
      raise TypeError()
    return self._cols_lower_bounds[i]

  def get_columns_lower_bounds(self):
    return self._cols_lower_bounds

  def get_columns_names(self):
    return self._cols_names

  def get_column_upper_bound(self, i):
    if not isinstance(i, int):
      raise TypeError()
    return self._cols_upper_bounds[i]

  def get_columns_upper_bounds(self):
    return self._cols_upper_bounds

  def get_column_name(self, i):
    if not isinstance(i, int):
      raise TypeError()
    return self._cols_names[i]

  def get_name(self):
    return self._name or self.DEFAULT_NAME

  def set_name(self, name):
    self._name = name

build = MPModelParameters.build
