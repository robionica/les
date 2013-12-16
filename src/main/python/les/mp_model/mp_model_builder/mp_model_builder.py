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

"""The :class:`~les.mp_model.mp_model.MPModel` represents mathematical
programming (MP) problem.

The following snippet shows how to build binary problem from scratch::

  import les
  model = les.build_model(
    # Objective function
    ([8., 2., 5., 5., 8., 3., 9., 7., 6.], True),
    # Matrix A
    [[2., 3., 4., 1., 0., 0., 0., 0., 0.],
     [1., 2., 3., 2., 0., 0., 0., 0., 0.],
     [0., 0., 1., 4., 3., 4., 2., 0., 0.],
     [0., 0., 2., 1., 1., 2., 5., 0., 0.],
     [0., 0., 0., 0., 0., 0., 2., 1., 2.],
     [0., 0., 0., 0., 0., 0., 3., 4., 1.]],
    # Senses
    ['L'] * 6,
    # Right-hand side
    [7, 6, 9, 7, 3, 5]
  )
  model.pprint()

Will print::

  maximize 8.0 * x1 + 2.0 * x2 + 5.0 * x3 + 5.0 * x4 + 8.0 * x5 + 3.0 * x6 +
           9.0 * x7 + 7.0 * x8 + 6.0 * x9
  s.t.
  c1: 2.0 * x1 + 3.0 * x2 + 4.0 * x3 + 1.0 * x4 <= 7.0
  c2: 1.0 * x1 + 2.0 * x2 + 3.0 * x3 + 2.0 * x4 <= 6.0
  c3: 1.0 * x3 + 4.0 * x4 + 3.0 * x5 + 4.0 * x6 + 2.0 * x7 <= 9.0
  c4: 2.0 * x3 + 1.0 * x4 + 1.0 * x5 + 2.0 * x6 + 5.0 * x7 <= 7.0
  c5: 2.0 * x7 + 1.0 * x8 + 2.0 * x9 <= 3.0
  c6: 3.0 * x7 + 4.0 * x8 + 1.0 * x9 <= 5.0

.. seealso:: http://en.wikipedia.org/wiki/Optimization_(mathematics)
"""

import os
import types
import collections
import gzip
import numpy
import types
import itertools
import re
import functools
from scipy import sparse
import sympy
from sympy.core import relational
import sys

from les import object_base
from les.mp_model import mp_model
from les.mp_model.knapsack_model import KnapsackModel
from les.mp_model.mp_model_builder.formats import mps
from les.mp_model.mp_model_builder import binary_mp_variable
from les.mp_model.mp_model_builder import mp_constraint
from les.mp_model.mp_model_builder import mp_objective
from les.mp_model.mp_model_builder import mp_variable
from les.utils import logging


_FORMAT_EXT_TO_DECODER_MAP = {
  '.mps': mps.Decoder
}

_SENSE_STR_TO_OPERATOR = {
  'L'  : relational.Le,
  'G'  : relational.Ge,
  'E'  : relational.Eq,

  '<=' : relational.Le,
  '<'  : relational.Lt,
  '>=' : relational.Ge,
  '>'  : relational.Gt,
}


class Error(Exception):
  pass


# TODO(d2rk): make global variable register to track MPVariable instances.
class MPModelBuilder(object):
  """The builder builds MP model instance."""

  DEFAULT_MODEL_NAME = "UNKNOWN"
  DEFAULT_OBJECTIVE_NAME = "OBJ"
  MODEL_NAME_FORMAT = "P%d"
  VARIABLE_NAME_FORMAT = "x{index}"
  VARIABLE_NAME_FORMAT_RE = re.compile(r"x\d+")
  CONSTRAINT_NAME_FORMAT = "c{index}"
  CONSTRAINT_NAME_FORMAT_RE = re.compile(r"c\d+")

  def __init__(self, variable_name_format=None,
               constraint_name_format=None):
    self._cons = collections.OrderedDict()
    self._cons_name_frmt = self.CONSTRAINT_NAME_FORMAT
    self._maximize = True
    self._name = None
    self._obj = None
    self._vars = collections.OrderedDict()
    self._var_name_frmt = self.VARIABLE_NAME_FORMAT
    if variable_name_format:
      self.set_variable_name_format(variable_name_format)
    if constraint_name_format:
      self.set_constraint_format(constraint_name_format)

  def add_binary_variable(self, *args, **kwargs):
    var = None
    if len(args) == 1 and isinstance(args[0], mp_variable.MPVariable):
      var = args[0]
    else:
      var = binary_mp_variable.BinaryMPVariable(*args, **kwargs)
    return self.add_variable(var)

  def add_variable(self, *args, **kwargs):
    """Adds new variable.

    :returns: :class:`~les.mp_model.mp_model_builder.mp_variable.MPVariable`
      instance.
    :raises: :exc:`TypeError`
    """
    var = None
    if len(args) == 1:
      if isinstance(args[0], mp_variable.MPVariable):
        var = args[0]
      else:
        var = binary_mp_variable.BinaryMPVariable(*args, **kwargs)
    else:
      var = mp_variable.MPVariable(*args, **kwargs)
    if not var.get_name():
      var.set_name(self.gen_variable_name(index=self.get_num_variables() + 1))
    if var.get_name() in self._vars:
      return
    # TODO(d2rk): how about to remove the variable?
    i = self.get_num_variables()
    var.set_index(i)
    self._vars[var.get_name()] = var
    return var

  def add_variables(self, variables):
    """Adds variables from iterable `variables`.

    .. seealso:: :func:`add_variable`
    """
    if not isinstance(variables, collections.Iterable):
      raise TypeError()
    for var in variables:
      self.add_variable(var)

  def add_constraint(self, *args, **kwargs):
    """Adds and returns a model constraint.

    Examples::

      c1 = model.add_constraint(2.0 * x + 3.0 * y <= 10.0, 'c1')
      c2 = model.add_constraint(3.0 * x, 'L', 8.0)

    :param expression: Left-hand side for new constraint.
    :param sense: Sense for new constraint.
    :param rhs: Right-hand side for new constraint.
    :param name: Constraint name.
    :return: A :class:`~les.mp_model.mp_constraint.MPConstraint` instance.
    """
    name = None
    cons = None
    if (len(args) in (1, 2) and
        not isinstance(args[0], mp_constraint.MPConstraint)):
      cons = mp_constraint.MPConstraint(args[0])
      name = args[1] if len(args) == 2 else kwargs.get('name', None)
    elif len(args) in (3, 4):
      sense = self.convert_sense_to_operator(args[1])
      cons = mp_constraint.MPConstraint(sense(args[0], args[2]))
      name = args[3] if len(args) == 4 else kwargs.get('name', None)
    else:
      raise Error()
    if not cons.get_name():
      if not name:
        name = self._cons_name_frmt.format(index=self.get_num_constraints() + 1)
      cons.set_name(name)
    # TODO(d2rk): fix the case when we remove the constraint.
    cons.set_index(self.get_num_constraints())
    self._cons[cons.get_name()] = cons
    return cons

  def build(self):
    objective = self.get_objective()
    if not objective:
      raise Error()
    m = self.get_num_constraints()
    n = self.get_num_variables()
    # Objective function...
    obj_coefs = [0.0] * n
    cols_lower_bounds = [0.0] * n
    cols_upper_bounds = [1.0] * n
    cols_names = [None] * n
    for var in self.get_variables():
      obj_coefs[var.get_index()] = objective.get_coefficient(var)
      cols_lower_bounds[var.get_index()] = var.get_lower_bound()
      cols_upper_bounds[var.get_index()] = var.get_upper_bound()
      cols_names[var.get_index()] = var.get_name()
    obj_name = objective.get_name()
    # Constraints coefficients, senses and right-hand side...
    rows_coefs = sparse.dok_matrix((m, n), dtype=float)
    rows_senses = []
    rows_rhs = [0.0] * m
    rows_names = [None] * m
    for constraint in self.get_constraints():
      i = constraint.get_index()
      for var in constraint.get_variables():
        rows_coefs[i, var.get_index()] = constraint.get_coefficient(var)
      rows_senses.append(constraint.get_sense())
      rows_rhs[i] = constraint.get_rhs()
      rows_names[i] = constraint.get_name()
    # Build MP model...
    return (mp_model.MPModel().
            set_name(self.get_name()).
            set_columns(cols_lower_bounds, cols_upper_bounds, cols_names).
            set_objective(obj_coefs, obj_name).
            set_rows(rows_coefs.tocsr(), rows_senses, rows_rhs,
                     rows_names))

  @classmethod
  def build_from(cls, *args, **kwargs):
    """Builds MP model instance from model parameters. This method tries to
    define model type and apply correct build method, such as
    :func:`build_from_mps`, :func:`build_from_scratch`,
    :func:`build_from_expressions`.

    :returns: A :class:`~les.mp_model.mp_model.MPModel` instance.
    :raises: :exc:`IOError`, :exc:`TypeError`

    .. seealso:: :func:`build_from_mps`, :func:`build_from_scratch`
    """
    if len(args) in (4, 5, 6, 7, 8):
      return cls.build_from_scratch(*args, **kwargs)
    elif len(args) in (2, 3):
      return cls.build_from_expressions(*args, **kwargs)
    if isinstance(args[0], mps.Decoder):
      return cls.build_from_mps(args[0])
    elif type(args[0]) is types.StringType:
      return cls.build_from_file(args[0])
    else:
      raise TypeError("Don't know how to handle this model.")

  @classmethod
  def build_from_file(cls, path):
    if not os.path.exists(path):
      raise IOError("File does not exist: %s" % path)
    root, ext = os.path.splitext(path)
    if path.endswith(".gz"):
      stream = gzip.open(path, "rb")
      root, ext = os.path.splitext(root)
    else:
      stream = open(path, "r")
    decoder_class = _FORMAT_EXT_TO_DECODER_MAP.get(ext)
    if not decoder_class:
      raise Error("Doesn't know how to read %s format. See available formats."
                  % ext)
    decoder = decoder_class()
    decoder.decode(stream)
    stream.close()
    return cls.build_from(decoder)

  @classmethod
  def build_from_expressions(cls, objective, constraints):
    model = mp_model.MPModel()
    model.set_objective(objective)
    model.set_constraints(constraints)
    return model

  @classmethod
  def build_from_mps(cls, decoder):
    """Builds a new model from MPS model.

    :param decoder: A :class:`~les.model.formats.mps.Decoder` instance.
    :returns: A :class:`MPModel` instance.
    """
    # TODO: fix this.
    logging.info("Read MPS format model from %s",
                 hasattr(decoder._stream, "name")
                 and getattr(decoder._stream, "name")
                 or type(decoder._stream))
    return (mp_model.MPModel()
            .set_name(decoder.get_name())
            .set_columns(decoder.get_columns_lower_bounds(),
                         decoder.get_columns_upper_bounds(),
                         decoder.get_columns_names())
            .set_objective(decoder.get_objective_coefficients(),
                           decoder.get_objective_name())
            .set_rows(decoder.get_rows_coefficients(),
                      decoder.get_rows_senses(),
                      decoder.get_rows_rhs(),
                      decoder.get_rows_names()))

  @classmethod
  def build_from_scratch(cls, objective_coefficients, constraints_coefficients,
                         constraints_senses, constraints_rhs,
                         constraints_names=[], variables_lower_bounds=[],
                         variables_upper_bounds=[], variables_names=[]):
    """Builds model from a scratch.

    The following code snippet shows how to define two models from scratch,
    where the first model needs to be maximized and the second one --
    minimized::

      MPModelBuilder.build_from_scratch([1, 1, 2], [[1, 2, 3], ['L', 'L'], [1, 1]])
      MPModelBuilder.build_from_scratch(([1, 1, 2], False), [[1, 2, 3], ['L', 'L'], [1, 1]])

    :param objective_coefficients: This parameter can be represented
      either a list of objective function variable coefficients, or a tuple,
      where the first element is a list of coefficients and the second one is
      ``True`` or ``False``, that defines objective function maximization or
      minimization. By default does maximization (see :func:`set_objective`).
    :param constraints_coefficients: Left-hand side or constraint matrix.
    :param constraints_senses: A list of senses of the constraints.
    :param constraints_rhs: A list of rhs bounds.
    :param constraints_names: A list of constraints names.
    :param variables_lower_bounds: A list of variables lower bounds.
    :param variables_upper_bounds: A list of variables upper bounds.
    :param variables_names: A list of variables names, where each name
      represented by a string.
    :returns: A :class:`MPModel` instance.

    :raises: :exc:`TypeError`
    """
    logging.debug('Build new model from scratch')
    if not bool(len(variables_names)):
      variables_names = []
      for i in range(1, len(objective_coefficients) + 1):
        variables_names.append(cls.VARIABLE_NAME_FORMAT.format(index=i))
    if not bool(len(variables_lower_bounds)):
      variables_lower_bounds = [0.0] * len(objective_coefficients)
    if not bool(len(variables_upper_bounds)):
      variables_upper_bounds = [1.0] * len(objective_coefficients)
    if not bool(len(constraints_names)):
      constraints_names = []
      for i in range(1, len(constraints_senses) + 1):
        constraints_names.append(cls.CONSTRAINT_NAME_FORMAT.format(index=i))
    return (mp_model.MPModel()
            .set_columns(variables_lower_bounds, variables_upper_bounds,
                         variables_names)
            .set_objective(objective_coefficients)
            .set_rows(constraints_coefficients, constraints_senses,
                      constraints_rhs, constraints_names))

  @classmethod
  def build_knapsack_model(cls, model):
    return (KnapsackModel()
            .set_columns(model.columns_lower_bounds,
                         model.columns_upper_bounds,
                         model.columns_names)
            .set_objective(model.objective_coefficients)
            .set_rows(model.rows_coefficients,
                      model.rows_senses,
                      model.rows_rhs,
                      model.rows_names))

  def build_protobuf(self):
    raise NotImplementedError()

  @classmethod
  def convert_sense_to_operator(cls, sense):
    if isinstance(sense, unicode):
      sense = str(sense)
    if type(sense) is types.BuiltinFunctionType:
      return sense
    elif not isinstance(sense, str):
      raise TypeError('Unknown sense type: ' + str(type(sense)))
    return _SENSE_STR_TO_OPERATOR[sense.upper()]

  @classmethod
  def convert_senses_to_operators(cls, senses):
    if not isinstance(senses, collections.Iterable):
      raise TypeError()
    operators = []
    for sense in senses:
      operators.append(cls.convert_sense_to_operator(sense))
    return operators

  def gen_variable_name(self, **kwargs):
    """Generates variable name."""
    return self._var_name_frmt.format(**kwargs)

  def get_constraint_by_index(self, i):
    """Returns constraint by the given index.

    :param i: An Integer.
    :returns: A :class:`~les.mp_model.mp_constraint.MPConstraint` instance.
    :raises: :exc:`TypeError`
    """
    if not isinstance(i, int):
      raise TypeError('i must be int: %s' % i)
    var = None
    if i < self.get_num_constraints():
      name, constraint = self._cons.items()[i]
    return constraint

  def get_constraints(self):
    """Returns a list of constraints.

    :returns: A list of :class:`~les.model.mp_constraint.MPConstraint`
      instances.
    """
    return self._cons.values()

  def get_name(self):
    """Returns the model name. Returns :attr:`DEFAULT_MODEL_NAME` if name wasn't
    defined.

    :returns: A string that represents model's name.
    """
    return self._name or self.__class__.DEFAULT_MODEL_NAME

  def get_num_constraints(self):
    """Returns the number of constraints."""
    return len(self._cons)

  def get_num_variables(self):
    """Returns the number of variables.

    :returns: The number of variables.
    """
    return len(self._vars)

  # TODO(d2rk): update objective function once new function has been added?
  def get_objective(self):
    """Returns objective function.

    :returns: An :class:`~les.model.mp_objective.MPObjective` instance.
    """
    return self._obj

  def get_objective_value(self):
    """Returns objective function value or `None` if it wasn't defined."""
    return self._obj and self._obj.get_value() or None

  def get_variables(self):
    """Return a list of presented variables.

    .. note:: The variables come in order they are stored in the constraint
              matrix.
    """
    return self._vars.values()

  def get_variable_by_name(self, name):
    """Returns variable by name or `None` if such variable cannot be found.

    :raises: :exc:`TypeError`
    """
    if not isinstance(name, unicode):
      raise TypeError('name must be a unicode: %s' % type(name))
    return self._vars.get(name, None)

  def get_variable_by_index(self, i):
    """Returns variable by the given index.

    :param i: An Integer.
    :returns: A :class:`~les.model.mp_variable.MPVariable` instance.
    :raises: :exc:`TypeError`
    """
    if not isinstance(i, int):
      raise TypeError('i must be int: %s' % i)
    var = None
    if i < self.get_num_variables():
      name, var = self._vars.items()[i]
    return var

  def maximize(self, expr, name=None):
    self.set_objective(expr, maximization=True, name=name)
    return self

  def minimize(self, expr):
    self.set_objective(expr, maximization=False)

  def is_binary(self):
    """Returns whether the model is binary integer linear programming
    model.

    :returns: `True` or `False`.
    """
    for var in self.get_variables():
      if not var.is_binary():
        return False
    return True

  def maximization(self):
    return self.get_objective().maximization()

  def set_maximization(self):
    self.get_objective().maximization()

  def set_minimization(self):
    self.get_objective().minimization()

  def pprint(self, file=sys.stdout):
    """Prints this model instance to the `file`.

    :param file: A stream.
    """
    if not self.get_num_variables():
      return
    file.write('%s ' % (self._maximize and 'maximize' or 'minimize',))
    file.write(str(self.get_objective()))
    file.write('\n')
    if not self.get_num_constraints():
      return
    file.write('s.t.\n')
    for cons in self.get_constraints():
      file.write('%s: %s' % (cons.get_name(), str(cons)))
      file.write('\n')

  def set_name(self, name):
    """Sets model name.

    :param name: A string that represents model name.
    :raises: :exc:`TypeError`
    """
    if not type(name) is types.StringType and not isinstance(name, unicode):
      raise TypeError('name must be a string or unicode: %s' % type(name))
    self._name = name
    return self

  def set_constraints(self, constraints):
    """Set constraints."""
    if not isinstance(constraints, collections.Iterable):
      raise TypeError()
    for constraint in constraints:
      self.add_constraint(constraint)
    return self

  def set_constraint_name_format(self, frmt):
    if frmt and type(frmt) is str:
      raise TypeError()
    self._cons_name_frmt = frmt

  # TODO: review this method.
  def set_objective(self, expr, maximization=True, name=None):
    """Set objective and optionaly its sense direction."""
    if not isinstance(expr, sympy.Expr):
      raise TypeError()
    for var in expr.atoms(sympy.Symbol):
      self.add_variable(var)
    self._obj = mp_objective.MPObjective(expr, maximization)
    self._obj.set_name(name or self.DEFAULT_OBJECTIVE_NAME)

  def __getattr__(self, name):
    if self.VARIABLE_NAME_FORMAT_RE.match(name):
      return functools.partial(self.add_variable, name)
    elif self.CONSTRAINT_NAME_FORMAT_RE.match(name):
      return functools.partial(self.add_constraint, name=name)

  def set_variable_name_format(self, frmt):
    if frmt and type(frmt) is str:
      raise TypeError('frmt must be a string: %s' % frmt)
    self._var_name_frmt = frmt

  def set_objective_from_scratch(self, coefficients, variables_names=[]):
    """Sets objective from a list/tuple of coefficients.

    :param coefficients: A list/tuple of coefficients.
    """
    self._obj = None
    if isinstance(coefficients, tuple) or isinstance(coefficients, list):
      coefficients = sparse.csr_matrix(numpy.matrix(coefficients), dtype=float)
    else:
      coefficients = sparse.csr_matrix(coefficients)
    add_variable = lambda i: self.add_variable(name=variables_names[i])
    if len(variables_names) == 0:
      add_variable = lambda i: self.add_variable()
    var = self.get_variable_by_index(coefficients.indices[0]) or add_variable(0)
    expr = float(coefficients.data[0]) * var
    for j, coefficient in itertools.izip(coefficients.indices[1:], coefficients.data[1:]):
      var = self.get_variable_by_index(j) or add_variable(j)
      expr += float(coefficient) * var
    self._obj = mp_objective.MPObjective(expr)

  def set_constraints_from_scratch(self, coefficients, senses, rhs, names=[]):
    """Sets constraints from scratch by the given coefficients matrix, list of
    constraint senses, list of right-hand side values, list of names.

    :param coefficients: Coefficients can be represented by a sparse matrix.
    :param senses: A list/tuple of senses of the constraints.
    :param rhs: Right-hand side. Can be represented by a list, tuple or vector.
    :param optional names: A list/tuple of names for new constraints.

    .. note:: The number of elements in `coefficients`, `senses`, `rhs` and
              `names` must be the same.
    """
    if isinstance(coefficients, numpy.matrix) or isinstance(coefficients, sparse.lil_matrix):
      coefficients = sparse.csr_matrix(coefficients)
    elif isinstance(coefficients, list):
      coefficients = sparse.csr_matrix(numpy.matrix(coefficients))
    if isinstance(rhs, tuple):
      rhs = list(rhs)
    if not isinstance(rhs, list):
      raise TypeError()
    # TODO(d2rk): Normalize senses.
    if coefficients.shape[0] != len(senses) or len(senses) != len(rhs):
      raise Error('%d != %d != %d' % (coefficients.shape[0], len(senses), len(rhs)))
    add_constraint = add_unnamed_constraint = lambda i, op, c: self.add_constraint(op(c, rhs[i]))
    add_named_constraint = lambda i, op, c: self.add_constraint(op(c, rhs[i]), name=names[i])
    if len(names):
      add_constraint = add_named_constraint
    for i, row in enumerate(coefficients):
      sense_operator = self.convert_sense_to_operator(senses[i])
      if not sense_operator:
        raise Error()
      var = self.get_variable_by_index(row.indices[0]) or self.add_variable()
      constraint = float(row.data[0]) * var
      # TODO(d2rk): it was row.indices[1:] but in this case we have a bug.
      for j, coefficient in itertools.izip(row.indices[1:], row.data[1:]):
        var = self.get_variable_by_index(j) or self.add_variable()
        constraint += float(coefficient) * var
      add_constraint(i, sense_operator, constraint)

  def slice(self, rows_scope, columns_scope):
    """Builds a submodel/slice on top of the another model."""
    submodel = mp_model.MPModel()
    # Build objective function and columns...
    columns_scope = sorted(list(columns_scope))
    rows_scope = list(rows_scope)
    col_coefs = []
    col_lower = []
    col_upper = []
    col_names = []
    for i in range(len(columns_scope)):
      var = self.get_variable_by_index(columns_scope[i])
      columns_scope[i] = var.get_name()
      col_lower.append(var.get_lower_bound())
      col_upper.append(var.get_upper_bound())
      col_names.append(var.get_name())
      col_coefs.append(self.get_objective().get_coefficient(var))
    submodel.set_objective_from_scratch(col_coefs)
    submodel.set_columns_from_scratch(col_lower, col_upper, col_names)
    # Build rows...
    row_senses = []
    row_rhs = []
    row_names = []
    row_coefs = sparse.dok_matrix((len(rows_scope), len(columns_scope)), dtype=float)
    for j in range(len(rows_scope)):
      constraint = self.get_constraint_by_index(rows_scope[j])
      row_names.append(constraint.get_name())
      row_rhs.append(constraint.get_rhs())
      row_senses.append(constraint.get_sense())
      for var in constraint.get_variables():
        if var.get_name() in columns_scope:
          row_coefs[j, columns_scope.index(var.get_name())] = constraint.get_coefficient(var)
    submodel.set_rows_from_scratch(row_coefs.tocsr(), row_senses, row_rhs, row_names)
    return submodel
