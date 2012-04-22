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

from les import mp_model
from les.mp_model import mp_model_parameters
from les.utils import generator_base

class Error(Exception):
  pass

class Generator(generator_base.GeneratorBase):
  '''The generator allows to generate relaxed models based on the given
  model.
  '''

  relaxed_model_name_format = '{model_name}_R{counter}'

  def __init__(self, model, shared_vars, local_vars):
    if not isinstance(model, mp_model.MPModel):
      raise TypeError()
    if not isinstance(shared_vars, tuple):
      raise TypeError('shared_vars should be a tuple: %s' % shared_vars)
    if not isinstance(local_vars, tuple):
      raise TypeError('local_vars should be a tuple: %s' % local_vars)
    if not len(shared_vars):
      raise Error('shared_vars cannot be empty.')
    if not all(isinstance(name, unicode) for name in shared_vars):
      raise TypeError()
    if not len(local_vars):
      raise Error('local_vars cannot be empty.')
    # TODO(d2rk): do we need to keep shared variables and local variables?
    self._shared_vars = shared_vars
    self._local_vars = local_vars
    self._shared_vars_indices = [model.get_variable_by_name(name).get_index()
                                 for name in shared_vars]
    self._local_vars_indices = [model.get_variable_by_name(name).get_index()
                                for name in local_vars]
    self._model = model
    self._model_params = params = mp_model_parameters.build(model)
    self._n = 1 << len(shared_vars)
    self._index = 0
    # TODO(d2rk): this is maximization pattern, add minimization pattern
    if model.maximization():
      self._mask_generator = xrange(self._n - 1, -1, -1)
    else:
      raise NotImplementedError()
    self._obj_coefs = []
    self._cols_names = []
    self._cols_lower_bounds = []
    self._cols_upper_bounds = []
    # Copy the model's local part.
    for i in self._local_vars_indices:
      self._obj_coefs.append(params.get_objective_coefficient(i))
      self._cols_names.append(params.get_column_name(i))
      self._cols_lower_bounds.append(params.get_column_lower_bound(i))
      self._cols_upper_bounds.append(params.get_column_upper_bound(i))

  def __str__(self):
    return '%s[size=%d]' % (self.__class__.__name__, self._n)

  def get_model(self):
    '''Returns model instance being the source of generation.'''
    return self._model

  def get_size(self):
    '''The final number of generated models.'''
    return self._n

  def has_next(self):
    '''Returns whether the next model can be generated.

    :returns: `True` or `False.`
    '''
    return self._index < self._n

  def next(self):
    '''Returns a model and base solution.

    :see: gen()
    :raises: :exc:`StopIteration`.
    '''
    if not self.has_next():
      raise StopIteration()
    model = self.gen(self._mask_generator[self._index])
    self._index += 1
    return model

  def gen(self, mask):
    '''Generates a model for a given mask. Note that the solution will include
    additional variables from the model.

    :return: a :class:`~les.model.Model` instance.
    :raises: :exc:`TypeError`
    '''
    if not type(mask) in (int, long):
      raise TypeError('mask can be an int or long: %s' % type(mask))
    solution = mp_model.MPSolution()
    solution.set_variables_values(self._model_params.get_columns_names(),
                                  [0.] * self._model_params.get_num_columns())
    rows_rhs = list(self._model_params.get_rows_rhs())
    rows_coefs = self._model_params.get_rows_coefficients().tocsc()
    for c, i in enumerate(self._shared_vars_indices):
      if not (mask >> c) & 1:
        continue
      for j in rows_coefs.getcol(i).nonzero()[0]:
        rows_rhs[j] -= rows_coefs[j, i]
      solution.get_variables_values()[i] = 1.0
    params = mp_model_parameters.build(
      self._obj_coefs,
      self._model_params.get_rows_coefficients()[:, self._local_vars_indices],
      self._model_params.get_rows_senses(),
      rows_rhs,
      self._cols_lower_bounds,
      self._cols_upper_bounds,
      self._cols_names)
    name = self.relaxed_model_name_format.format(model_name=self._model.get_name(),
                                                 counter=self._index)
    params.set_name(name)
    return (params, solution)
