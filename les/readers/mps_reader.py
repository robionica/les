# -*- coding: utf-8; -*-
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

"""MPS (Mathematical Programming System) is a file format for presenting and
archiving linear programming (LP) and mixed integer programming problems.

Read more about format specs: <http://en.wikipedia.org/wiki/MPS_(format)>,
<http://lpsolve.sourceforge.net/5.5/mps-format.htm>.
"""

import numpy
from scipy import sparse
import re
import bz2
import gzip
import types

from les.readers.reader import Reader

_MTS_FORMAT_REGEX = re.compile(r"""
^NAME\s+(\w+)\s*\n
ROWS\s*\n
 ([-+\w\s\d]+)\s*\n
COLUMNS\s*\n
 ([-+\w\s\d]+)\s*\n
RHS\s*\n
 ([-+\w\s\d]+)\s*\n
BOUNDS\s*\n
 ([-+\w\s\d]+)\s*\n
ENDATA\s*$
""", re.M | re.X)

_ROWS_ENTRY_REGEX = re.compile("^\s+(\w)\s+(\w+)\s*$")
_COLS_ENTRY_REGEX = re.compile("^\s+(\w+)\s+(\w+)\s+([+-]*\d+)(\s+(\w+)\s+([+-]*\d+))*\s*$")
_RHS_ENTRY_REGEX = re.compile("^\s+(\w+)\s+(\w+)\s+([+-]*\d+)(\s+(\w+)\s+([+-]*\d+))*\s*$")

class MPSReader(Reader):
  """This class represents MPS-format problem reader."""

  def __init__(self):
    Reader.__init__(self)
    self._name = None
    self._row_register = {}
    self._rows_senses = []
    self._col_register = {}
    self._con_coefs = []
    self._rhs_register = {}
    self._rhs = []

  def parse(self, stream):
    if isinstance(stream, (types.FileType, bz2.BZ2File, gzip.GzipFile)):
      data = stream.read()
    elif isinstance(stream, types.StringType):
      data = stream
    else:
      raise TypeError()
    result = re.match(_MTS_FORMAT_REGEX, data)
    if not result:
      raise Exception()
    self._name = result.group(1)
    self._process_section(result.group(2), self._parse_rows_section)
    self._process_section(result.group(3), self._parse_cols_section)
    self._process_section(result.group(4), self._parse_rhs_section)
    self._process_section(result.group(5), self._parse_bounds_section)

  def _process_section(self, section, callback):
    # Split by lines, filter empty lines and comments
    lines = filter(lambda line: len(line) and not line.startswith("*"),
                   section.split("\n"))
    callback(lines)

  def get_rhs(self):
    return self._rhs

  def get_name(self):
    return self._name

  def get_con_coefs(self):
    return self._con_coefs

  def get_rows_senses(self):
    return self._rows_senses

  def _parse_bounds_section(self, lines):
    pass

  def _parse_rhs_section(self, lines):
    self._rhs_register = {}
    for line in lines:
      result = re.match(_RHS_ENTRY_REGEX, line)
      if not result:
        break
      rhs_name, row_name, v = result.group(1), result.group(2), result.group(3)
      if not rhs_name in self._rhs_register:
        self._rhs_register[rhs_name] = len(self._rhs_register)
        self._rhs.append([0.0] * len(self._row_register))
      rhs_id = self._rhs_register[rhs_name]
      self._rhs[rhs_id][self._row_register[row_name]] = float(v)
      if result.group(4):
        row_name, v = result.group(5), result.group(6)
        self._rhs[rhs_id][self._row_register[row_name]] = float(v)

  def _parse_cols_section(self, lines):
    self._col_register = {}
    self._con_coefs = []
    for line in lines:
      result = re.match(_COLS_ENTRY_REGEX, line)
      if not result:
        break
      col_name, row_name, v = result.group(1), result.group(2), result.group(3)
      j = self._col_register.setdefault(col_name, len(self._col_register))
      self._con_coefs.append((self._row_register[row_name], j, float(v)))
      if result.group(4):
        row_name, v = result.group(5), result.group(6)
        self._con_coefs.append((self._row_register[row_name], j, float(v)))

  def _parse_rows_section(self, lines):
    self._row_register = {}
    self._rows_senses = []
    for line in lines:
      result = re.match(_ROWS_ENTRY_REGEX, line)
      if result:
        sense, name = result.group(1), result.group(2)
        if name in self._row_register:
          raise Exception("%s was already registered" % name)
        self._row_register[name] = len(self._row_register)
        self._rows_senses.append(sense)
      else:
        break
