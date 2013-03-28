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

from les.problems.bilp_problem import BILPProblem
from les.readers.reader import Reader

class MPSReader(Reader):

  _NAME_SECTION = re.compile("^NAME\s+(\w+)$")
  _ROWS_SECTION = re.compile("^ROWS\s*$")
  _ROWS_ENTRY = re.compile("^\s+(\w)\s+(\w+)\s*$")
  _COLS_SECTION = re.compile("^COLUMNS\s*$")
  _COLS_ENTRY = re.compile("^\s+(\w+)\s+(\w+)\s+([+-]*\d+)(\s+(\w+)\s+([+-]*\d+))*\s*$")
  _RHS_SECTION = re.compile("^RHS$")
  _RHS_ENTRY = re.compile("^\s+(\w+)\s+(\w+)\s+([+-]*\d+)(\s+(\w+)\s+([+-]*\d+))*\s*$")

  def __init__(self):
    Reader.__init__(self)

  def reset(self):
    self._rows = dict()
    self._cols = dict()
    self._vals = []
    self._rhs = []
    self._lines = []

  def build_problem(self):
    # Build A from scratch. Use dok format.
    A = sparse.dok_matrix((len(self._rows), len(self._cols)),
                          dtype=numpy.float16)
    for i, j, v in self._vals:
      A[i, j] = v
    A = A.tocsr()
    problem = BILPProblem(A[0,:].todense(),
                          True,
                          A[1:,:],
                          [],
                          self._rhs[1:],
                          [])
    return problem

  def parse(self, stream):
    self.reset()
    if isinstance(stream, (types.FileType, bz2.BZ2File, gzip.GzipFile)):
      self._lines = stream.readlines()
    elif isinstance(stream, types.StringType):
      self._lines = stream.split("\n")
    else:
      raise TypeError()
    self._pos = 0
    # Filter empty lines and comments
    self._lines = filter(lambda line: len(line) and not line.startswith("*"),
                         self._lines)
    self._process_name_section()
    self._process_rows_section()
    self._process_cols_section()
    self._process_rhs_section()

  def _process_rhs_section(self):
    for self._pos in range(self._pos + 1, len(self._lines), 1):
      if re.match(self._RHS_SECTION, self._lines[self._pos]):
        break
    for self._pos in range(self._pos + 1, len(self._lines), 1):
      result = re.match(self._RHS_ENTRY, self._lines[self._pos])
      if result:
        rhs_name, row_name, v = result.group(1), result.group(2), result.group(3)
        self._rhs[self._rows[row_name][0]] = float(v)
        if result.group(4):
          row_name, v = result.group(5), result.group(6)
          self._rhs[self._rows[row_name][0]] = float(v)
      else:
        break
    self._pos -= 1

  def _process_cols_section(self):
    for self._pos in range(self._pos + 1, len(self._lines), 1):
      if re.match(self._COLS_SECTION, self._lines[self._pos]):
        break
    for self._pos in range(self._pos + 1, len(self._lines), 1):
      result = re.match(self._COLS_ENTRY, self._lines[self._pos])
      if result:
        col_name, row_name, v = result.group(1), result.group(2), result.group(3)
        j = self._cols.setdefault(col_name, len(self._cols))
        self._vals.append((self._rows[row_name][0], j, float(v)))
        if result.group(4):
          row_name, v = result.group(5), result.group(6)
          self._vals.append((self._rows[row_name][0], j, float(v)))
      else:
        break
    self._pos -= 1

  def _process_rows_section(self):
    for self._pos in range(self._pos + 1, len(self._lines), 1):
      if re.match(self._ROWS_SECTION, self._lines[self._pos]):
        break
    for self._pos in range(self._pos + 1, len(self._lines), 1):
      result = re.match(self._ROWS_ENTRY, self._lines[self._pos])
      if result:
        sense, name = result.group(1), result.group(2)
        self._rows[name] = (len(self._rows), sense)
      else:
        break
    self._pos -= 1
    self._rhs = [0.0] * len(self._rows)

  def _process_name_section(self):
    for self._pos in range(self._pos, len(self._lines), 1):
      result = re.match(self._NAME_SECTION, self._lines[self._pos])
      if result:
        name = result.group(1)
        break
    self._name = name
