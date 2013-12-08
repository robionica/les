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

import gzip
import os
import types
from scipy import sparse

from les.mp_model import mp_model
from les.mp_model import mp_model_parameters
from les.mp_model.formats import mps
from les.utils import logging

_FORMAT_EXT_TO_DECODER_MAP = {
  '.mps': mps.Decoder
}

class MPModelBuilder(object):
  '''The builder builds MP model instances.'''

  @classmethod
  def build_submodel(cls, model, rows_scope, columns_scope):
    """Builds a submodel/slice on top of the another model."""
    submodel = mp_model_parameters.MPModelParameters()
    # Build objective function and define columns.
    columns_scope = sorted(list(columns_scope))
    rows_scope = list(rows_scope)
    col_coefs = []
    col_lower = []
    col_upper = []
    col_names = []
    for i in range(len(columns_scope)):
      var = model.get_variable_by_index(columns_scope[i])
      columns_scope[i] = var.get_name()
      col_lower.append(var.get_lower_bound())
      col_upper.append(var.get_upper_bound())
      col_names.append(var.get_name())
      col_coefs.append(model.get_objective().get_coefficient(var))
    submodel.set_objective_from_scratch(col_coefs)
    submodel.set_columns_from_scratch(col_lower, col_upper, col_names)
    # Build rows.
    row_senses = []
    row_rhs = []
    row_names = []
    row_coefs = sparse.dok_matrix((len(rows_scope), len(columns_scope)), dtype=float)
    for j in range(len(rows_scope)):
      constraint = model.get_constraint_by_index(rows_scope[j])
      row_names.append(constraint.get_name())
      row_rhs.append(constraint.get_rhs())
      row_senses.append(constraint.get_sense())
      for var in constraint.get_variables():
        if var.get_name() in columns_scope:
          row_coefs[j, columns_scope.index(var.get_name())] = constraint.get_coefficient(var)
    submodel.set_rows_from_scratch(row_coefs.tocsr(), row_senses, row_rhs, row_names)
    return submodel

  @classmethod
  def build(cls, *args, **kwargs):
    '''Builds MP model instance from model parameters. This method tries to
    define model type and apply correct build method, such as
    :func:`build_from_mps`, :func:`build_from_scratch`,
    :func:`build_from_expressions`.

    :returns: A :class:`~les.mp_model.mp_model.MPModel` instance.
    :raises: :exc:`IOError`, :exc:`TypeError`

    .. seealso:: :func:`build_from_mps`, :func:`build_from_scratch`
    '''
    if not len(args) and not len(kwargs):
      return mp_model.MPModel()
    elif len(args) == 4:
      return cls.build_from_scratch(*args, **kwargs)
    elif len(args) in (2, 3):
      return cls.build_from_expressions(*args, **kwargs)
    model = args[0]
    if isinstance(model, mps.Decoder):
      return cls.build_from_mps(model)
    elif type(model) is types.StringType:
      if not os.path.exists(model):
        raise IOError('File does not exist: %s' % model)
      root, ext = os.path.splitext(model)
      if model.endswith('.gz'):
        stream = gzip.open(model, 'rb')
        root, ext = os.path.splitext(root)
      else:
        stream = open(model, 'r')
      decoder_class = _FORMAT_EXT_TO_DECODER_MAP.get(ext)
      if not decoder_class:
        raise Error("Doesn't know how to read %s format. See available formats."
                    % ext)
      decoder = decoder_class()
      decoder.decode(stream)
      stream.close()
      return cls.build(decoder)
    else:
      raise TypeError('Do not know how to handle this model.')

  @classmethod
  def build_from_expressions(cls, objective, constraints):
    model = mp_model.MPModel()
    model.set_objective(objective)
    model.set_constraints(constraints)
    return model

  @classmethod
  def build_from_mps(cls, decoder):
    '''Builds a new model from MPS model.

    :param decoder: A :class:`~les.model.formats.mps.Decoder` instance.
    :returns: A :class:`MPModel` instance.
    '''
    # TODO: fix this.
    logging.info('Read MPS format model from %s',
                 hasattr(decoder._stream, 'name') and getattr(decoder._stream, 'name') or
                 type(decoder._stream))
    model = mp_model.MPModel()
    model.set_name(decoder.get_name())
    model.set_objective_from_scratch(decoder.get_objective_coefficients(),
                                     decoder.get_columns_names())
    model.set_constraints_from_scratch(decoder.get_rows_coefficients(),
                                       decoder.get_rows_senses(),
                                       decoder.get_rows_rhs(),
                                       decoder.get_rows_names())
    return model

  # TODO: add constraints_names.
  @classmethod
  def build_from_scratch(cls, objective_coefficients, constraints_coefficients,
                         constraints_senses, constraints_rhs,
                         variables_lower_bounds=[],
                         variables_upper_bounds=[], variables_names=[]):
    '''Builds model from a scratch.

    The following code snippet shows how to define two models from scratch,
    where the first model needs to be maximized and the second one --
    minimized::

      MPModel.build_from_scratch([1, 1, 2], [[1, 2, 3], ['L', 'L'], [1, 1]])
      MPModel.build_from_scratch(([1, 1, 2], False), [[1, 2, 3], ['L', 'L'],
                                  [1, 1]])

    :param objective_coefficients: This parameter can be represented
      either a list of objective function variable coefficients, or a tuple,
      where the first element is a list of coefficients and the second one is
      ``True`` or ``False``, that defines objective function maximization or
      minimization. By default does maximization (see :func:`set_objective`).
    :param constraints_coefficients: Left-hand side or constraint matrix.
    :param constraints_senses: A list of senses of the constraints.
    :param constraints_rhs: A list of rhs bounds.
    :param variables_lower_bounds: A list of variables lower bounds.
    :param variables_upper_bounds: A list of variables upper bounds.
    :param variables_names: A list of variables names, where each name
      represented by a string.
    :returns: A :class:`MPModel` instance.

    :raises: :exc:`TypeError`
    '''
    logging.debug('Build new model from scratch')
    model = mp_model.MPModel()
    model.set_objective_from_scratch(objective_coefficients, variables_names)
    model.set_constraints_from_scratch(constraints_coefficients,
                                       constraints_senses, constraints_rhs)
    return model
