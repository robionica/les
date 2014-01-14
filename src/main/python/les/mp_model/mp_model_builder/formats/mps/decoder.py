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

import bz2
import gzip
import types
from scipy import sparse
import string
import StringIO

from les.utils import logging


COMMENT = '*'


class Decoder(object):
  '''This class represents MPS-format model decoder.'''

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
      self.decode(filename_or_stream)

  def _get_next_line(self):
    self._line = self._buffer.readline()
    return self._line

  def _get_line_fields(self):
    return self._line.split()

  def decode(self, filename_or_stream):
    '''Parses a file or stream and decodes the model.

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
    self.decode_from_string(data)

  def decode_from_string(self, data):
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
        self._decode_rows_section_entry()
      elif section_name == 'COLUMNS':
        self._decode_columns_section_entry()
      elif section_name == 'RHS':
        self._decode_rhs_section_entry()
      elif section_name == 'BOUNDS':
        self._decode_bounds_section_entry()
      else:
        logging.error('Unknown section: %s', section_name)
        break
    # TODO: we have to to remove last empty column from the matrix. Can we avoid
    # this?
    self._rows_coefs = self._rows_coefs[0:self._rows_coefs.shape[0],
                                        0:self._rows_coefs.shape[1] - 1]

  def _decode_bounds_section_entry(self):
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

  def _decode_rows_section_entry(self):
    sense, name = self._line.split()
    if sense == 'N':
      self._obj_name = name
      return
    self._rows_senses.append(str(sense))
    self._rows_names.append(str(name))
    self._rows_coefs = self._rows_coefs.reshape((len(self._rows_names),
                                                 self._rows_coefs.shape[1]))
    self._rows_rhs.append(None)

  def _decode_columns_section_entry(self):
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

  def _decode_rhs_section_entry(self):
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

  def get_columns_lower_bounds(self):
    return self._cols_lower_bounds

  def get_columns_upper_bounds(self):
    return self._cols_upper_bounds

  def get_objective_coefficients(self):
    return self._obj_coefs

  def get_objective_name(self):
    return self._obj_name

  def get_rows_senses(self):
    '''Returns a list of rows senses.'''
    return self._rows_senses

  def get_rows_names(self):
    return self._rows_names

  def get_rows_coefficients(self):
    return self._rows_coefs
