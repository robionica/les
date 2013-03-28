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

"""In binary problems, each variable can only take on the value of 0 or 1. This
may represent the selection or rejection of an option, the turning on or off
of switches, a yes/no answer, or many other situations.

    :math:`f(x) = \\sum_{j=1}^{n}{c_{j}x_{j}}{ \\rightarrow max}`

        subject to

    :math:`\\sum_{j=1}^{n}{a_{ij}x_j \\leq b_i, \quad i=\\overline{1,m}},
    \quad x_j=\{0,1\}, \quad j=\\overline{1,n}`

"""

import os
import numpy as np
from scipy import sparse
import gzip
import types

from les.sparse_vector import SparseVector
from les.problems.problem import Problem
from les.readers.mps_reader import MPSReader

_READERS = {
  ".mps": MPSReader
}

__all__ = ["BILPProblem", "ZOLPProblem"]

class BILPProblem(Problem):
  """This class represents generic binary integer linear programming (BILP)
  problem or zero-one linear programming (ZOLP) problem.
  """

  def __init__(self, obj_coefs=[], maximaze=True, cons_matrix=None,
               rows_senses=[], rows_upper_bounds=[], rows_lower_bounds=[]):
    self._obj_coefs = None
    self.set_obj_coefs(obj_coefs)
    self._cons_matrix = None
    self._set_cons_matrix(cons_matrix)
    self._rows_senses = rows_senses
    self._rows_upper_bounds = None
    self.set_rows_upper_bounds(rows_upper_bounds)

  @classmethod
  def build(cls, data):
    if isinstance(data, MPSReader):
      return cls._build_from_mps(data)
    elif type(data) is types.StringType:
      # The file name has been provided. Detect reader and read the problem.
      if not os.path.exists(data):
        raise IOError("File doesn't exist: %s" % data)
      root, ext = os.path.splitext(data)
      if data.endswith(".gz"):
        stream = gzip.open(data, "rb")
        root, ext = os.path.splitext(root)
      else:
        stream = open(data, "r")
      reader_class = _READERS.get(ext)
      if not reader_class:
        raise Exception("Doesn't know how to read %s format."
                        "See available formats."
                        % ext)
      reader = reader_class()
      reader.parse(stream)
      stream.close()
      return cls.build(reader)
    else:
      raise TypeError("Don't know how to handle this data")

  @classmethod
  def _build_from_mps(cls, reader):
    # Build A from scratch. Use dok format.
    A = sparse.dok_matrix((len(reader._row_register), len(reader._col_register)),
                          dtype=np.float16)
    for i, j, v in reader.get_con_coefs():
      A[i, j] = v
    A = A.tocsr()
    rhs = reader.get_rhs()[0]
    if not len(rhs) == A.shape[0]:
      raise Exception()
    problem = BILPProblem(A[0,:].todense(),
                          True,
                          A[1:,:],
                          [],
                          rhs[1:],
                          [])
    return problem

  def build_subproblem(self, *args, **kwargs):
    return BILPSubproblem(self, *args, **kwargs)

  def get_num_rows(self):
    """Returns the number of rows."""
    return self._cons_matrix.shape[0]

  def get_num_cols(self):
    """Returns the number of columns."""
    return self._cons_matrix.shape[1]

  def _set_cons_matrix(self, m):
    if isinstance(m, np.matrix):
      self._cons_matrix = sparse.csr_matrix(m)
    else:
      self._cons_matrix = m

  def set_obj_coefs(self, coefs):
    if isinstance(coefs, (tuple, list)):
      obj = sparse.dok_matrix((1, len(coefs)), dtype=np.float16)
      for i, c in enumerate(coefs):
        obj[0, i] = c
    else:
      obj = coefs
    self._obj_coefs = SparseVector(obj)

  def get_obj_coefs(self):
    return self._obj_coefs

  def get_rows_upper_bounds(self):
    return self._rows_upper_bounds

  def set_row_upper_bound(self, i, v):
    """Set a single row upper bound."""
    self._rows_upper_bounds[i] = v

  def set_row_bounds(self, lower, upper):
    """Set a single row lower and upper bound."""
    pass

  def set_rows_upper_bounds(self, values):
    """Set rows upper bounds."""
    if isinstance(values, sparse.dok_matrix):
      self._rows_upper_bounds = SparseVector(values)
    elif isinstance(values, (tuple, list)):
      m = sparse.dok_matrix((1, len(values)), dtype=np.float16)
      for i, c in enumerate(values):
        m[0, i] = c
      self._rows_upper_bounds = SparseVector(m)
    elif isinstance(values, SparseVector):
      self._rows_upper_bounds = values
    else:
      raise TypeError()

  def get_cons_matrix(self):
    return self._cons_matrix

  def check_col_solution(self, solution):
    # TODO: solution can be a tuple, list or sparse.base.spmatrix
    if len(solution) != self.get_num_cols():
      raise Exception("%d != %d" % (solution.shape[1], self.get_num_cols()))
    v = self._cons_matrix.dot(solution)
    for i in range(len(v)):
      # TODO: add sense
      if v[i] > self._rows_upper_bounds[i]:
        return False
    return True

ZOLPProblem = BILPProblem

class BILPSubproblem(BILPProblem):

  def __init__(self, problem, obj=[], maximaze=True, cons_matrix=None,
               cons_senses=[], upper_bounds=[], shared_cols=[]):
    BILPProblem.__init__(self, obj, maximaze, cons_matrix, cons_senses,
                         upper_bounds)
    self._name = None
    self._problem = problem
    self._shared_cols = shared_cols
    self._local_cols = set(cons_matrix.nonzero()[1]) - shared_cols
    self._deps = dict()

  def __str__(self):
    return "%s[num_shared_cols=%d, num_local_cols=%d]" \
        % (self._name, len(self._shared_cols), len(self._local_cols))

  def _set_name(self, name):
    """Sets subproblem name. Done automatically by solver."""
    if not isinstance(name, str):
      raise TypeError()
    self._name = name

  def get_name(self):
    return self._name

  def get_shared_cols(self):
    return self._shared_cols

  def get_local_cols(self):
    return self._local_cols

  def get_dependencies(self):
    return self._deps

  def add_dependency(self, subproblem, shared_cols):
    if not isinstance(shared_cols, set):
      raise TypeError("shared_cols must be a set")
    if not len(shared_cols):
      raise Exception("No shared cols")
    self._deps[subproblem] = shared_cols
