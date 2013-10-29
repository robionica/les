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

from les.mp_model import mp_model
from les.mp_model import mp_model_parameters

_SYMPY_MPS_SENSE_MAPPING = {
  '<=': 'L',
  '>=': 'G',
  '==': 'E',
}

class Encoder(object):
  '''Encodes a MPS value to a stream.

  :param filename_or_stream: A filename or stream.

  Example

  Suppose we'd like to write a MP model such as the following::

    model = mp_model.build(
      [8, 2, 5, 5, 8, 3, 9, 7, 6],
      [[2, 3, 4, 1, 0, 0, 0, 0, 0],
       [1, 2, 3, 2, 0, 0, 0, 0, 0],
       [0, 0, 1, 4, 3, 4, 2, 0, 0],
       [0, 0, 2, 1, 1, 2, 5, 0, 0],
       [0, 0, 0, 0, 0, 0, 2, 1, 2],
       [0, 0, 0, 0, 0, 0, 3, 4, 1]],
      ['L'] * 6,
      [7, 6, 9, 7, 3, 5])

  This code writes the above model and prints the encoded value::

    stream = StringIO.StringIO()
    writer = mps.Writer(stream)
    writer.write(model)
    print stream.getvalue()
  '''

  def __init__(self, filename_or_stream, model=None):
    self._stream = None
    if isinstance(filename_or_stream, str):
      self._stream = open(filename_or_stream, 'w+b')
    elif isinstance(filename_or_stream, object):
      self._stream = filename_or_stream
    else:
      raise TypeError()
    if model:
      self.encode(model)

  def encode(self, model):
    if isinstance(model, mp_model.MPModel):
      self._encode_mp_model(model)
    else:
      raise TypeError()

  def _encode_mp_model_parameters(self, params):
    self._stream.write('NAME %s\n' % params.get_name())
    # Write ROWS section.
    self._stream.write('ROWS\n')
    self._stream.write('\tN\t%s\n' % params.get_objective_name())
    for i in range(params.get_num_rows()):
      self._stream.write('\t%s\t%s\n'
                         % (_SYMPY_MPS_SENSE_MAPPING[params.get_rows_senses()[i]],
                            params.get_rows_names()[i]))
    # Write COLUMNS section.
    self._stream.write('COLUMNS\n')
    cols_coefs = params.get_rows_coefficients().tocsc()
    for i in range(params.get_num_columns()):
      col = cols_coefs.getcol(i)
      self._stream.write('\t%s' % (params.get_columns_names()[i],))
      self._stream.write('\t%s %d' % (params.get_objective_name(),
                                      params.get_objective_coefficient(i)))
      row_indices, col_indices = col.nonzero()
      counter = 1
      for ii, ij in zip(row_indices, col_indices):
        if not counter % 2:
          self._stream.write('\t%s' % (params.get_columns_names()[i],))
        self._stream.write('\t%s %d' % (params.get_rows_names()[ii], col[ii, ij]))
        counter += 1
        if not counter % 2:
          self._stream.write('\n')
      if counter % 2:
        self._stream.write('\n')
    # Write RHS section.
    counter = 0
    self._stream.write('RHS\n')
    for i in range(params.get_num_rows()):
      if not counter % 2:
        # TODO: fix rhs enumeration.
        self._stream.write('\tRHS1\t')
      self._stream.write('%s\t%d\t' % (params.get_rows_names()[i],
                                       params.get_rows_rhs()[i]))
      counter += 1
      if not counter % 2:
        self._stream.write('\n')
    if counter % 2:
      self._stream.write('\n')
    # Write BOUNDS section.
    # TODO: fix bounds.
    self._stream.write('BOUNDS\n')
    for i in params.get_columns_indices():
      self._stream.write('\tUP BND1 %s %d\n' % (params.get_columns_names()[i],
                                                params.get_column_upper_bound(i)))
      self._stream.write('\tLO BND1 %s %d\n' % (params.get_columns_names()[i],
                                                params.get_column_lower_bound(i)))
    self._stream.write('ENDATA')

  def _encode_mp_model(self, model):
    self._encode_mp_model_parameters(mp_model_parameters.build(model))
