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

from sympy.core import relational

from les import object_base
from les.mp_model.mp_model_builder import mp_variable


_SYMPY_MPS_SENSE_MAPPING = {
  "<=": "L",
  ">=": "G",
  "==": "E",
}


class MPConstraint(object_base.ObjectBase):
  """This class represents model constraint."""

  def __init__(self, expr):
    # TODO(d2rk): check expr type.
    if not isinstance(expr, relational.Relational):
      raise TypeError('expr must be Relational: %s' % type(expr))
    self._name = None
    self._expr = expr
    self._index = None

  def __repr__(self):
    return ('%s[name=%s, index=%d, num_variables=%d, sense="%s", rhs=%f]'
            % (self.__class__.__name__, self._name, self._index,
               len(self.get_variables()), self.get_sense(), self.get_rhs()))

  def __str__(self):
    return str(self._expr)

  def get_coefficient(self, var):
    if not isinstance(var, mp_variable.MPVariable):
      raise TypeError()
    return float(self._expr.lhs.coeff(var))

  def get_index(self):
    """Returns constraint index in the list of model constraints."""
    return self._index

  def get_name(self):
    """Returns constraint name."""
    return self._name

  def get_rhs(self):
    """Returns constraint right-hand side value."""
    return float(self._expr.rhs or self._expr.lhs)

  def get_sense(self):
    return _SYMPY_MPS_SENSE_MAPPING[self._expr.rel_op]

  def get_variables(self):
    """Returns list of variables from this constraint.

    :returns: A list of :class:`les.model.mp_variable.MPVariable` instances.
    """
    return self._expr.lhs.atoms(mp_variable.MPVariable)

  def set_index(self, i):
    if not isinstance(i, int):
      raise TypeError()
    self._index = i

  def set_name(self, name):
    if not isinstance(name, str):
      raise TypeError()
    self._name = name
