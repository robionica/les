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

'''The enumerator generates candidate models based on the given domain model
(submodel). The **candidate model** associated with a partial solution to an
BILP model is the restricted model obtained by fixing the binary variables as in
the partial solution.

A ``partial solution`` has some discrete decision variables fixed, while other
left free.

However, if we have `n` binary variables, we might have to perform ``2**m``
models.

The following example shows how to build and print all models of model ``m``,
that has ``shared_vars`` as shared variables and ``local_vars`` as local
variables::

  enumerator = SharedVariablesEnumerator(m, shared_vars, local_vars)
  for m in enumerator:
    print m

.. note::

   :class:`SharedVariablesEnumerator` works only with BILP models.
'''

from les import mp_model
from les.mp_model import mp_model_parameters
from les.utils import generator_base


class Error(Exception):
  pass


class _Template:

  def __init__(self):
    self.objective_coefficients = []
    self.columns_names = []
    self.columns_lower_bounds = []
    self.columns_upper_bounds = []


class SharedVariablesEnumerator(generator_base.GeneratorBase):
  '''This class represents generator allows to generate relaxed models based on
  the given BILP model.

  :param model: A :class:`~les.mp_model.mp_model.MPModel` instance.
  :param shared_vars: A list of strings, where each string represents a name of
    a shared variable.
  :param local_vars: A list of strings, where each string represents a name of
    a local variable.
  :raises: :exc:`TypeError`, :exc:`Error`.
  '''

  model_name_format = '{source_model_name}_E{counter}'

  def __init__(self, original_model, shared_vars, local_vars):
    # TODO(d2rk): do we need to keep shared variables and local variables?
    self._model = None
    self._model_params = None
    self._shared_vars = []
    self._local_vars = []
    self._shared_vars_indices = []
    self._local_vars_indices = []
    self._set_domain_model(original_model, shared_vars, local_vars)

  def __str__(self):
    return '%s[size=%d]' % (self.__class__.__name__, self._n)

  def _set_domain_model(self, domain_model, shared_vars, local_vars):
    if not isinstance(domain_model, mp_model.MPModel):
      raise TypeError()
    if not domain_model.is_binary():
      raise TypeError('Enumerator works only with BILP models.')
    if not isinstance(shared_vars, tuple) and not isinstance(shared_vars, set):
      raise TypeError('shared_vars should be a tuple: %s' % shared_vars)
    if not isinstance(local_vars, tuple) and not isinstance(shared_vars, set):
      raise TypeError('local_vars should be a tuple: %s' % local_vars)
    if not len(shared_vars):
      raise Error('shared_vars cannot be empty.')
    if not all(isinstance(name, unicode) for name in shared_vars):
      raise TypeError()
    if not len(local_vars):
      raise Error('local_vars cannot be empty.')
    self._shared_vars = shared_vars
    self._local_vars = local_vars
    try:
      self._shared_vars_indices = [domain_model.get_variable_by_name(name).get_index()
                                   for name in shared_vars]
      self._local_vars_indices = [domain_model.get_variable_by_name(name).get_index()
                                  for name in local_vars]
    except AttributeError:
      raise Error('Domain model does not containt this variable: %s' % name)
    self._model = domain_model
    self._model_params = params = mp_model_parameters.build(domain_model)
    self._n = 1 << len(shared_vars)
    self._index = 0
    # TODO(d2rk): this is maximization pattern, add minimization pattern
    if domain_model.maximization():
      self._mask_generator = xrange(self._n - 1, -1, -1)
    else:
      raise NotImplementedError()
    self._template = template = _Template()
    # Copy the local part of domain model.
    for i in self._local_vars_indices:
      template.objective_coefficients.append(params.get_objective_coefficient(i))
      template.columns_names.append(params.get_column_name(i))
      template.columns_lower_bounds.append(params.get_column_lower_bound(i))
      template.columns_upper_bounds.append(params.get_column_upper_bound(i))

  def gen_candidate_model(self, mask):
    '''Generates a candidate model and partial solution for it by the given
    mask.

    :param mask: An integer that represents a mask of variables assignment.
    :returns: a tuple of :class:`~les.mp_model.mp_model.MPModel` instance and
    :class:`~les.mp_model.mp_solution.MPSolution` instance.
    :raises: :exc:`TypeError`

    Assume we have a model ``m`` that has variables `x1`, `x2`, `x3`,
    `x4`, `x5`, where `x1`, `x3` are local variables and `x3`, `x4`, `x5` are
    shared variables::

      e = SharedVariablesEnumerator(m, [u'x3', u'x4', u'x5'], [u'x1', u'x2'])
      m5, s5 = e.gen_candidate_model(5)  # 101

    As the result, the model ``m5`` contains two variables `x1` and `x2`, while
    `x3`, `x4` and `x5` were substituted by 1, 0, and 1 respectively.
    '''
    if not type(mask) in (int, long):
      raise TypeError('mask can be an int or long: %s' % type(mask))
    solution_base = mp_model.MPSolution()
    solution_base.set_variables_values(self._model_params.get_columns_names(),
                                       [0.] * self._model_params.get_num_columns())
    rows_rhs = list(self._model_params.get_rows_rhs())
    rows_coefs = self._model_params.get_rows_coefficients().tocsc()
    for c, i in enumerate(self._shared_vars_indices):
      if not (mask >> c) & 1:
        continue
      for j in rows_coefs.getcol(i).nonzero()[0]:
        rows_rhs[j] -= rows_coefs[j, i]
      solution_base.get_variables_values()[i] = 1.0
    model_params = mp_model_parameters.build(
      self._template.objective_coefficients,
      self._model_params.get_rows_coefficients()[:, self._local_vars_indices],
      self._model_params.get_rows_senses(),
      rows_rhs,
      self._template.columns_lower_bounds,
      self._template.columns_upper_bounds,
      self._template.columns_names)
    name = self.model_name_format.format(
      source_model_name=self._model.get_name(), counter=self._index)
    model_params.set_name(name)
    return (model_params, solution_base)

  def get_domain_model(self):
    '''Returns model instance being the domain model of generation.

    :returns: A :class:`~les.mp_model.mp_model.MPModel` instance.
    '''
    return self._model

  def get_size(self):
    '''The final number of generated models.'''
    return self._n

  def has_next(self):
    '''Returns whether the next model can be generated.

    :returns: ``True`` or ``False``.
    '''
    return self._index < self._n

  def next(self):
    '''Returns a model and base solution.

    :see: :func:`gen`.
    :raises: :exc:`StopIteration`.
    '''
    if not self.has_next():
      raise StopIteration()
    model = self.gen_candidate_model(self._mask_generator[self._index])
    self._index += 1
    return model
