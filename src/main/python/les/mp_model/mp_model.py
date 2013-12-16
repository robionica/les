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

import numpy
from scipy import sparse
import string
import sys

from les.utils import logging
from les.utils import uuid
from les import object_base


class Error(Exception):
  pass


class MPModel(object_base.ObjectBase):
  """The model of mathmatical programming problem consists of a set of variables
  (where a variable is represented by
  :class:`~les.model.mp_variable.MPVariable`) and a set of constraints (where a
  constraint is represented by :class:`~les.model.mp_constraint.MPConstraint`).

  By default maximization is set.

  :param name: Optional string that represents model name.
  :param variable_name_format: A string that represents a format that will be
    used to automitically generate variable names if they were not provided,
    e.g. `x0`, `x1`, etc.
  :param constraint_name_format: A string that represents a format that will be
    used to automitically generate constraint names if they were not provided,
    e.g. `c0`, `c1`, etc.
  """

  def __init__(self, name=None):
    self._name = name or uuid.ShortUUID().uuid()
    self._maximization = True
    self.objective_coefficients = []
    self.objective_name = None
    self.objective_value = None
    self.columns_lower_bounds = []
    self.columns_upper_bounds = []
    self.columns_names = []
    self.columns_values = []
    self.rows_names = []
    self.rows_coefficients = None
    self.rows_rhs = []
    self.rows_senses = []

  def __str__(self):
    return ("%s[num_rows=%d, num_columns=%d, maximization=%s]" %
            (self.__class__.__name__, self.get_num_rows(),
             self.get_num_columns(), self.maximization()))

  def get_objective_value(self):
    return self.objective_value

  def set_solution(self, solution):
    self.objective_value = solution.get_objective_value()
    # TODO(d2rk): set only triggered variables.
    for i in range(self.get_num_columns()):
      name = self.columns_names[i]
      if name in solution.get_variables_names():
        self.columns_values[i] = solution.get_variable_value_by_name(name)

  def is_binary(self):
    """Returns whether the model is binary integer linear programming
    model.

    :returns: `True` or `False`.
    """
    for i in range(len(self.objective_coefficients)):
      if (self.columns_lower_bounds[i] != 0.0
          or self.columns_upper_bounds[i] != 1.0):
        return False
    return True

  def optimize(self, params=None):
    """Optimize the model by using given optimization parameters.

    :param params: A OptimizationParameters instance.
    """
    from les.frontend_solver import FrontendSolver
    solver = FrontendSolver()
    solver.load_model(self)
    solver.solve(params)

  def set_columns(self, columns_lower_bounds=[], columns_upper_bounds=[],
                  columns_names=[]):
    if (len(columns_lower_bounds) != len(columns_upper_bounds)
        or len(columns_upper_bounds) != len(columns_names)):
      raise ValueError("upper bounds == lower bounds == names: %d == %d == %d"
                       % (len(columns_lower_bounds), len(columns_upper_bounds),
                          len(columns_names)))
    self.columns_lower_bounds = columns_lower_bounds
    self.columns_upper_bounds = columns_upper_bounds
    self.columns_names = columns_names
    self.columns_values = [0.0] * len(columns_names)
    return self

  def set_objective(self, coefficients, name=None):
    if isinstance(coefficients, tuple):
      self.objective_coefficients = list(coefficients)
    if not isinstance(coefficients, list):
      raise TypeError("coefficients: %s" % coefficients)
    self.objective_coefficients = coefficients
    self.objective_name = name
    return self

  def set_objective_name(self, name):
    self.objective_name = name

  def set_rows(self, coefficients, senses, rhs, names=[]):
    # Normalize matrix of coefficients
    if isinstance(coefficients, list):
      coefficients = numpy.matrix(coefficients, dtype=float)
    if isinstance(coefficients, numpy.matrix):
      coefficients = sparse.csr_matrix(coefficients, dtype=float)
    else:
      coefficients = coefficients.tocsr()
    # Normalize RHS
    if isinstance(rhs, (tuple, list)):
      rhs = list(rhs)
    else:
      raise TypeError()
    # TODO(d2rk): Normalize senses.
    if (coefficients.shape[0] != len(senses) or
        len(senses) != len(rhs)):
      raise Exception()
    if len(names) and len(names) != len(rhs):
      raise Exception()
    elif not len(names):
      names = [None] * len(rhs)
    self.rows_coefficients = coefficients
    self.rows_senses = senses
    self.rows_rhs = rhs
    self.rows_names = names
    return self

  def maximization(self):
    return self._maximization

  def minimization(self):
    return self._minimization

  def check_columns_values(self, columns_values):
    """Checks whether the given columns values are correct.

    :param columns_values: A list of column values.

    :returns: ``True`` or ``False``.
    """
    raise NotImplementedError()
    # TODO: solution can be a tuple, list or sparse.base.spmatrix
    if type(columns_values) in (tuple, list):
      columns_values = numpy.array(columns_values)
    if columns_values.shape[0] != self.get_num_columns():
      logging.warning("Number of columns values doesn't match number of "
                      "columns: %d != %d", columns_values.shape[0],
                      self.get_num_columns())
      return False
    v = self.rows_coefficients.dot(columns_values)
    for i in xrange(len(v)):
      # TODO: add sense.
      if not v[i] <= self.rows_rhs[i]:
        return False
    return True

  def get_status(self):
    return None

  @classmethod
  def status_to_string(self):
    return None

  def is_feasible(self):
    return False

  def is_optimal(self):
    return False

  def is_optimal_or_feasible(self):
    return self.is_optimal() or self.is_feasible()

  def get_num_columns(self):
    return self.rows_coefficients.shape[1]

  def get_columns_indices(self):
    return range(len(self.objective_coefficients))

  def get_num_rows(self):
    return self.rows_coefficients.shape[0]

  def get_objective_coefficients(self):
    return self.objective_coefficients

  def get_objective_coefficient(self, i):
    return self.objective_coefficients[i]

  def get_objective_name(self):
    return self.objective_name

  def get_rows_coefficients(self):
    """Returns matrix of constraints coefficients.

    :returns: A :class:`scipy.sparse.csr_matrix` instance. By default returns
      ``None``.
    """
    return self.rows_coefficients

  def get_rows_names(self):
    """Returns list of rows names."""
    return self.rows_names

  def get_row_name(self, i):
    return len(self.rows_names) and self.rows_names[i] or None

  def get_rows_rhs(self):
    """Returns vector that represents right-hand side."""
    return self.rows_rhs

  def get_rows_senses(self):
    return self.rows_senses

  def get_column_lower_bound(self, i):
    if not isinstance(i, int):
      raise TypeError()
    return self.columns_lower_bounds[i]

  def get_columns_lower_bounds(self):
    return self.columns_lower_bounds

  def get_columns_names(self):
    return self.columns_names

  def get_column_upper_bound(self, i):
    if not isinstance(i, int):
      raise TypeError()
    return self.columns_upper_bounds[i]

  def get_columns_upper_bounds(self):
    return self.columns_upper_bounds

  def get_column_name(self, i):
    if not isinstance(i, int):
      raise TypeError()
    return self.columns_names[i]

  def get_name(self):
    return self._name

  def set_name(self, name):
    self._name = name
    return self

  def slice(self, rows_scope, columns_scope):
    """Builds a submodel/slice based on this model."""
    columns_scope = list(columns_scope)
    rows_scope = list(rows_scope)
    return (self.__class__()
             .set_columns([self.columns_lower_bounds[_] for _ in columns_scope],
                          [self.columns_upper_bounds[_] for _ in columns_scope],
                          [self.columns_names[_] for _ in columns_scope])
             .set_objective([self.objective_coefficients[_] for _ in columns_scope],
                            self.objective_name)
             .set_rows(self.rows_coefficients[rows_scope, :][:, columns_scope],
                       [self.rows_senses[_] for _ in rows_scope],
                       [self.rows_rhs[_] for _ in rows_scope],
                       [self.rows_names[_] for _ in rows_scope]))

  def pprint(self, file=sys.stdout):
    if bool(len(self.objective_coefficients)):
      file.write("%s: %s" % (self.objective_name, self._maximization
                             and "maximize" or "minimize"))
      for i in range(len(self.objective_coefficients)):
        file.write(" %+.20g %s" % (self.objective_coefficients[i],
                                   self.columns_names[i]))
      file.write("\n")
    if bool(self.rows_coefficients.shape[0]):
      file.write("s.t.\n")
      for i in range(self.rows_coefficients.shape[0]):
        file.write("%s:" % self.rows_names[i])
        row = self.rows_coefficients.getrow(i)
        for ii, ij in zip(*row.nonzero()):
          file.write(" %+.20g %s" % (row[ii, ij], self.columns_names[ij]))
        file.write(" %s %+.20g" % (self.rows_senses[i], self.rows_rhs[i]))
        file.write("\n")
