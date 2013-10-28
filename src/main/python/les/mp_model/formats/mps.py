#!/usr/bin/env python
#
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

'''MPS (Mathematical Programming System) is a file format for presenting and
archiving linear programming (LP) and mixed integer programming problems.

Read more about format specs:

* <http://en.wikipedia.org/wiki/MPS_(format)>
* <http://lpsolve.sourceforge.net/5.5/mps-format.htm>
* <http://www.gurobi.com/documentation/5.5/reference-manual/node900>
'''

from scipy import sparse
import bz2
import gzip
import types
import string
import StringIO

from les.utils import logging

COMMENT = '*'

class Reader(object):
  '''This class represents MPS-format problem reader.'''

  def __init__(self, filename_or_stream=None):
    self._cols_names = []
    self._cols_upper_bounds = []
    self._cols_lower_bounds = []
    self._line = None
    self._name = None
    self._obj_name = None
    self._obj_coefs = []
    self._rows_senses = []
    self._rows_names = []
    self._rows_coefs = sparse.lil_matrix((1, 1), dtype=float)
    self._rows_rhs = []
    self._stream = None
    if filename_or_stream:
      self.parse(filename_or_stream)

  def _get_next_line(self):
    self._line = self._buffer.readline()
    return self._line

  def _get_line_fields(self):
    return self._line.split()

  def parse(self, filename_or_stream):
    '''Parses a file or stream.

    :param filename_or_stream: A string that represents filename or data or
      stream object.
    :raises: :exc:`TypeError`
    '''
    if isinstance(filename_or_stream, str):
      with open(filename_or_stream, 'r') as stream:
        self._stream = stream
        data = stream.read()
    elif isinstance(filename_or_stream, (types.FileType, bz2.BZ2File,
                                         gzip.GzipFile)):
      self._stream = filename_or_stream
      data = filename_or_stream.read()
    elif isinstance(filename_or_stream, StringIO.StringIO):
      self._stream = filename_or_stream
      data = filename_or_stream.getvalue()
    elif isinstance(filename_or_stream, types.StringType):
      data = filename_or_stream
    else:
      raise TypeError()
    self.parse_from_string(data)

  def parse_from_string(self, data):
    '''Parses problem from given string.'''
    if not isinstance(data, str) and not isinstance(data, unicode):
      raise TypeError('data must be a string or unicode: %s' % type(data))
    if len(data) == 0:
      raise ValueError()
    self._buffer = StringIO.StringIO(data)
    section_name = None
    def get_first_word():
      for i in range(len(self._line)):
        if self._line[i] in string.whitespace: break
      return self._line[0:i]
    while self._get_next_line():
      if not len(self._line.strip()) or self._line.strip().startswith(COMMENT):
        continue
      if self._line[0] in string.letters:
        section_name = get_first_word()
        if section_name == 'NAME':
          fields = self._line.split()
          self._name = fields[1]
        elif section_name == 'ENDATA':
          break
        continue
      fields = self._get_line_fields()
      if fields[1] == "'MARKER'":
        if fields[2] == "'INTORG'":
          self._marker_name = fields[0]
        elif fields[2] == "'INTEND'":
          self._marker_name = fields[0]
        else:
          logging.error('Unknown marker')
        continue
      if section_name == 'ROWS':
        self._parse_rows_section_entry()
      elif section_name == 'COLUMNS':
        self._parse_columns_section_entry()
      elif section_name == 'RHS':
        self._parse_rhs_section_entry()
      elif section_name == 'BOUNDS':
        self._parse_bounds_section_entry()
      else:
        logging.error('Unknown section: %s', section_name)
        break
    # TODO: we have to to remove last empty column from the matrix. Can we avoid
    # this?
    self._rows_coefs = self._rows_coefs[0:self._rows_coefs.shape[0],
                                        0:self._rows_coefs.shape[1] - 1]

  def _parse_bounds_section_entry(self):
    fields = self._get_line_fields()
    i = self._cols_names.index(fields[2])
    if fields[0] == 'LO':
      self._cols_lower_bounds[i] = float(fields[3])
    elif fields[0] == 'UP':
      self._cols_upper_bounds[i] = float(fields[3])
    elif fields[0] == 'FX':
      self._cols_lower_bounds[i] = self._cols_upper_bounds[i] = float(fields[3])
    elif fields[0] == 'BV':
      self._cols_lower_bounds[i] = 0.0
      self._cols_upper_bounds[i] = 1.0
    else:
      raise Exception()

  def _parse_rows_section_entry(self):
    sense, name = self._line.split()
    if sense == 'N':
      self._obj_name = name
      return
    self._rows_senses.append(str(sense))
    self._rows_names.append(str(name))
    self._rows_coefs = self._rows_coefs.reshape((len(self._rows_names),
                                                 self._rows_coefs.shape[1]))
    self._rows_rhs.append(None)

  def _parse_columns_section_entry(self):
    fields = self._line.split()
    column_name, row_name, value = unicode(fields[0]), unicode(fields[1]), fields[2]
    try:
      j = self._cols_names.index(column_name)
    except ValueError:
      j = len(self._cols_names)
      self._cols_names.append(str(column_name))
      self._rows_coefs = sparse.hstack([self._rows_coefs, sparse.lil_matrix((self._rows_coefs.shape[0], 1), dtype=float)]).tolil()
      self._cols_lower_bounds.append(0.0)
      self._cols_upper_bounds.append(0.0)
    # Update objective function vector if row name equals to objective function
    # name.
    if row_name == self._obj_name:
      self._obj_coefs.append(float(value))
      if len(fields) > 3:
        self._rows_coefs[self._rows_names.index(fields[3]), j] = float(fields[4])
      return
    self._rows_coefs[self._rows_names.index(row_name), j] = float(value)
    if len(fields) > 3:
      self._rows_coefs[self._rows_names.index(fields[3]), j] = float(fields[4])

  def _parse_rhs_section_entry(self):
    fields = self._get_line_fields()
    rhs_name, row_name, value = unicode(fields[0]), unicode(fields[1]), float(fields[2])
    self._rows_rhs[self._rows_names.index(row_name)] = value
    if len(fields) > 3:
      self._rows_rhs[self._rows_names.index(fields[3])] = float(fields[4])

  def get_rows_rhs(self):
    '''Returns a list that represents right-hand side.'''
    return self._rows_rhs

  def get_name(self):
    '''Returns problem name.'''
    return self._name

  def get_columns_names(self):
    return self._cols_names

  def get_objective_coefficients(self):
    return self._obj_coefs

  def get_rows_senses(self):
    '''Returns a list of rows senses.'''
    return self._rows_senses

  def get_rows_names(self):
    return self._rows_names

  def get_rows_coefficients(self):
    return self._rows_coefs

_SYMPY_MPS_SENSE_MAPPING = {
  '<=': 'L',
  '>=': 'G',
  '==': 'E',
}

class Writer(object):
  '''Writes a MPS encoded value to a stream.

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
      self.write(model)

  def write(self, model):
    from les import mp_model
    if isinstance(model, mp_model.MPModel):
      self._write_mp_model(model)
    else:
      raise TypeError()

  def _write_mp_model_parameters(self, params):
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

  def _write_mp_model(self, model):
    from les.mp_model import mp_model_parameters
    self._write_mp_model_parameters(mp_model_parameters.build(model))

def read(filename_or_stream):
  return Reader(filename_or_stream)

def write(filename_or_stream, data):
  return Writer(filename_or_stream, data)
