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

from sympy.core import expr as sympy_expr

from les import object_base
from les.mp_model import mp_variable

class MPObjective(object_base.ObjectBase, object_base.Cloneable):
  '''This class represents objective function:

    obj = Objective(5 * x + 6 * y, True)
  '''

  def __init__(self, expr, maximization=True):
    if not isinstance(expr, sympy_expr.Expr):
      raise TypeError()
    self._name = None
    self._expr = expr
    self._maximization = maximization
    self._value = None

  def __str__(self):
    return str(self._expr)

  def clone(self):
    variables = list(self.get_variables())
    expr = self.get_coefficient(variables[0]) * variables[0].clone()
    for i in range(1, len(variables)):
      expr += self.get_coefficient(variables[i]) * variables[i].clone()
    return Objective(expr, self.maximization())

  def get_name(self):
    return self._name

  def maximization(self):
    return self._maximization

  def minimization(self):
    return not self._maximization

  def get_coefficient(self, var):
    '''Gets variable coefficient in this objective function.

    :param var: A :class:`~les.mp_model.mp_variable.MPVariable` instance.
    :returns: `float`.
    :raises: :exc:`TypeError`
    '''
    if not isinstance(var, mp_variable.MPVariable):
      raise TypeError()
    return float(self._expr.coeff(var))

  def get_variables(self):
    return self._expr.atoms(mp_variable.MPVariable)

  def get_value(self):
    '''Get objective function value.

    :returns: An Integer or `None`.
    '''
    return self._value

  def set_coefficient(self, i, v):
    raise NotImplementedError()

  def set_maximization(self):
    self._maximization = True

  def set_minimization(self):
    self._maximization = False

  def set_name(self, name):
    if not isinstance(name, str):
      raise TypeError()
    self._name = name

  def set_value(self, value):
    if not isinstance(value, float):
      raise TypeError()
    self._value = value
