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

'''The :class:`MPModel` represents mathematical programming (MP) problem.

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
'''

from __future__ import absolute_import

import collections
import numpy
import sympy
from sympy.core import relational
import sys
import types
import itertools
from scipy import sparse

from les import object_base
from les.mp_model import binary_mp_variable
from les.mp_model import mp_constraint
from les.mp_model import mp_objective
from les.mp_model import mp_variable
from les.utils import logging

SENSE_STR_TO_OPERATOR = {
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
class MPModel(object_base.ObjectBase):
  '''The model of mathmatical programming problem consists of a set of variables
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
  '''

  default_model_name = 'UNKNOWN'
  model_name_format = 'P%d'
  variable_name_format = 'x{index}'
  constraint_name_format = 'c{index}'
  default_objective_name = 'OBJ'

  def __init__(self, name=None, variable_name_format=None,
               constraint_name_format=None):
    self._cons = collections.OrderedDict()
    self._cons_name_frmt = self.constraint_name_format
    self._maximize = True
    self._name = None
    self._obj = None
    self._vars = collections.OrderedDict()
    self._var_name_frmt = self.variable_name_format
    if variable_name_format:
      self.set_variable_name_format(variable_name_format)
    if constraint_name_format:
      self.set_constraint_format(constraint_name_format)
    if name:
      self.set_name(name)

  def __str__(self):
    return '%s[name=%s, num_constraints=%d, num_variables=%d]' \
        % (self.__class__.__name__, self.get_name(), self.get_num_constraints(),
           self.get_num_variables())

  def add_constraint(self, *args, **kwargs):
    '''Adds and returns a model constraint.

    Examples::

      c1 = model.add_constraint(2.0 * x + 3.0 * y <= 10.0, 'c1')
      c2 = model.add_constraint(3.0 * x, 'L', 8.0)

    :param expression: Left-hand side for new constraint.
    :param sense: Sense for new constraint.
    :param rhs: Right-hand side for new constraint.
    :param name: Constraint name.
    :return: A :class:`les.model.mp_constraint.MPConstraint` instance.
    '''
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

  def add_variables(self, variables):
    '''Adds variables from iterable `variables`.

    .. seealso:: :func:`add_variable`
    '''
    if not isinstance(variables, collections.Iterable):
      raise TypeError()
    for var in variables:
      self.add_variable(var)

  def add_variable(self, *args, **kwargs):
    '''Adds new variable.

    :returns: :class:`~les.model.mp_variable.MPVariable` instance.
    :raises: :exc:`TypeError`
    '''
    var = None
    if len(args) == 1 and isinstance(args[0], mp_variable.MPVariable):
      var = args[0]
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

  def add_binary_variable(self, *args, **kwargs):
    var = None
    if len(args) == 1 and isinstance(args[0], mp_variable.MPVariable):
      var = args[0]
    else:
      var = binary_mp_variable.BinaryMPVariable(*args, **kwargs)
    return self.add_variable(var)

  @classmethod
  def convert_sense_to_operator(cls, sense):
    if isinstance(sense, unicode):
      sense = str(sense)
    if type(sense) is types.BuiltinFunctionType:
      return sense
    elif not isinstance(sense, str):
      raise TypeError('Unknown sense type: ' + str(type(sense)))
    return SENSE_STR_TO_OPERATOR[sense.upper()]

  @classmethod
  def convert_senses_to_operators(cls, senses):
    if not isinstance(senses, collections.Iterable):
      raise TypeError()
    operators = []
    for sense in senses:
      operators.append(cls.convert_sense_to_operator(sense))
    return operators

  def gen_variable_name(self, **kwargs):
    '''Generates variable name.'''
    return self._var_name_frmt.format(**kwargs)

  def get_constraints(self):
    '''Returns a list of constraints.

    :returns: A list of :class:`~les.model.mp_constraint.MPConstraint`
      instances.
    '''
    return self._cons.values()

  def get_name(self):
    '''Returns the model name. Returns :attr:`default_model_name` if name wasn't
    defined.

    :returns: A string that represents model's name.
    '''
    return self._name or self.__class__.default_model_name

  def get_num_constraints(self):
    '''Returns the number of constraints.'''
    return len(self._cons)

  def get_num_variables(self):
    '''Returns the number of variables.

    :returns: The number of variables.
    '''
    return len(self._vars)

  # TODO(d2rk): update objective function once new function has been added?
  def get_objective(self):
    '''Returns objective function.

    :returns: An :class:`~les.model.mp_objective.MPObjective` instance.
    '''
    return self._obj

  def get_objective_value(self):
    '''Returns objective function value or `None` if it wasn't defined.'''
    return self._obj and self._obj.get_value() or None

  def get_status(self):
    return None

  @classmethod
  def status_to_string(self):
    return None

  def get_variables(self):
    '''Return a list of presented variables.

    .. note:: The variables come in order they are stored in the constraint
              matrix.
    '''
    return self._vars.values()

  def get_variable_by_name(self, name):
    '''Returns variable by name or `None` if such variable cannot be found.

    :raises: :exc:`TypeError`
    '''
    if not isinstance(name, unicode):
      raise TypeError('name must be a unicode: %s' % type(name))
    return self._vars.get(name, None)

  def get_variable_by_index(self, i):
    '''Returns variable by the given index.

    :param i: An Integer.
    :returns: A :class:`~les.model.mp_variable.MPVariable` instance.
    :raises: :exc:`TypeError`
    '''
    if not isinstance(i, int):
      raise TypeError('i must be int: %s' % i)
    var = None
    if i < self.get_num_variables():
      name, var = self._vars.items()[i]
    return var

  def maximize(self, expr):
    self.set_objective(expr, maximization=True)

  def minimize(self, expr):
    self.set_objective(expr, maximization=False)

  def optimize(self, optimization_params=None):
    '''Optimize the model by using given optimization parameters.'''
    from les import frontend_solver
    solver = frontend_solver.FrontendSolver()
    solver.load_model(self)
    solver.solve(params=optimization_params)

  def is_binary(self):
    '''Returns whether the model is binary integer linear programming
    model.

    :returns: `True` or `False`.
    '''
    for var in self.get_variables():
      if not var.is_binary():
        return False
    return True

  def is_feasible(self):
    return False

  def is_optimal(self):
    return False

  def is_optimal_or_feasible(self):
    return self.is_optimal() or self.is_feasible()

  def maximization(self):
    return self.get_objective().maximization()

  def set_maximization(self):
    self.get_objective().maximization()

  def set_minimization(self):
    self.get_objective().minimization()

  def pprint(self, file=sys.stdout):
    '''Prints this model instance to the `file`.

    :param file: A stream.
    '''
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
    '''Sets model name.

    :param name: A string that represents model name.
    :raises: :exc:`TypeError`
    '''
    if not type(name) is types.StringType and not isinstance(name, unicode):
      raise TypeError('name must be a string or unicode: %s' % type(name))
    self._name = name

  def set_constraints(self, constraints):
    '''Set constraints.'''
    if not isinstance(constraints, collections.Iterable):
      raise TypeError()
    for constraint in constraints:
      self.add_constraint(constraint)

  def set_constraint_name_format(self, frmt):
    if frmt and type(frmt) is str:
      raise TypeError()
    self._cons_name_frmt = frmt

  # TODO: review this method.
  def set_objective(self, expr, maximization=True):
    '''Set objective and optionaly its sense direction.'''
    if not isinstance(expr, sympy.Expr):
      raise TypeError()
    for var in expr.atoms(sympy.Symbol):
      self.add_variable(var)
    self._obj = mp_objective.MPObjective(expr, maximization)
    self._obj.set_name(self.default_objective_name)

  def set_variable_name_format(self, frmt):
    if frmt and type(frmt) is str:
      raise TypeError('frmt must be a string: %s' % frmt)
    self._var_name_frmt = frmt

  def set_objective_from_scratch(self, coefficients, variables_names=[]):
    '''Sets objective from a list/tuple of coefficients.

    :param coefficients: A list/tuple of coefficients.
    '''
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
    '''Sets constraints from scratch by the given coefficients matrix, list of
    constraint senses, list of right-hand side values, list of names.

    :param coefficients: Coefficients can be represented by a sparse matrix.
    :param senses: A list/tuple of senses of the constraints.
    :param rhs: Right-hand side. Can be represented by a list, tuple or vector.
    :param optional names: A list/tuple of names for new constraints.

    .. note:: The number of elements in `coefficients`, `senses`, `rhs` and
              `names` must be the same.
    '''
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
    if names:
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
