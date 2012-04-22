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

import uuid
import sympy

from les import object_base

class Error(Exception):
  pass

class Term(sympy.Dummy, object_base.ObjectBase, object_base.Cloneable):

  def __new__(meta_class, *args, **kwargs):
    return sympy.Dummy.__new__(meta_class, str(uuid.uuid1()))

# TODO(d2rk): remove objective_coefficient.
class MPVariable(Term):
  '''This class represents the base variable type. Variables are always
  associated with a particular problem model.

  :param lower_bound: Lower bound for new variable.
  :param upper_bound: Upper bound for new variable.
  :param vtype: Variable type: MPVariable.BINARY.
  :param name: Variable name.
  '''

  VAR_TYPE_RANGE = range(2)
  (BINARY, INTEGER) = VAR_TYPE_RANGE

  def __init__(self, lower_bound=0.0, upper_bound=1.0, vtype=INTEGER,
               name=None):
    Term.__init__(self)
    # NOTE: separate variable name from term name.
    self._name = None
    self._index = 0
    self._value = 0.0
    self._lower_bound = None
    self._upper_bound = None
    self._vtype = None
    self.set_type(vtype)
    self.set_lower_bound(lower_bound)
    self.set_upper_bound(upper_bound)
    if self._lower_bound > self._upper_bound:
      raise Error()
    if name:
      self.set_name(name)

  def __str__(self):
    return ('%s[name="%s", index=%d, lower_bound=%f, upper_bound=%f, vtype=%s]'
            % (self.__class__.__name__, self.get_name(), self.get_index(),
               self.get_lower_bound(), self.get_upper_bound(), self._vtype))

  def _fix_vtype(self):
    if self._lower_bound == 0.0 and self._upper_bound == 1.0:
      self._vtype = self.BINARY

  def clone(self):
    other = MPVariable(self.get_lower_bound(), self.get_upper_bound(),
                       self._vtype)
    other.set_name(self.get_name())
    # TODO(d2rk): do not copy index attribute.
    return other

  def is_binary(self):
    '''Returns whether this variable is binary variable.

    :returns: `True` or `False`.
    '''
    return self._vtype is self.BINARY

  def get_name(self):
    '''Returns the name of the variable.'''
    return self._name

  def get_upper_bound(self):
    '''Returns the variable upper bound value.'''
    return self._upper_bound

  def get_lower_bound(self):
    '''Returns the variable lower bound value.'''
    return self._lower_bound

  def get_value(self):
    return self._value

  def get_index(self):
    return self._index

  def set_type(self, vtype):
    if vtype and not vtype in self.VAR_TYPE_RANGE:
      raise Error('Unknown variable type: ' + str(vtype))
    if vtype is self.BINARY:
      self._lower_bound = 0.0
      self._upper_bound = 1.0
    self._vtype = vtype

  def set_name(self, name):
    if isinstance(name, str):
      name = unicode(name)
    if not type(name) is unicode:
      raise TypeError('name must be a unicode: %s' % type(name))
    self._name = self.name = name

  def set_lower_bound(self, bound):
    if not isinstance(bound, float):
      raise TypeError()
    self._lower_bound = bound
    self._fix_vtype()

  def set_upper_bound(self, bound):
    if not isinstance(bound, float):
      raise TypeError()
    self._upper_bound = bound
    self._fix_vtype()

  def set_index(self, i):
    if not isinstance(i, int):
      raise TypeError()
    self._index = i

  def set_value(self, value):
    if not isinstance(value, float):
      raise TypeError()
    self._value = value
