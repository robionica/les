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

import numpy as np
from scipy.sparse import csr_matrix, lil_matrix, dok_matrix
from scipy.sparse.base import spmatrix

from les.sparse_vector import SparseVector

class Problem(object):

  subproblem_name_format = "Z%d"

  def __init__(self, obj=[], cons_matrix=None, cons_senses=[], upper_bounds=[]):
    self._obj = None
    self.set_obj_coefs(obj)
    self._cons_matrix = None
    self._set_cons_matrix(cons_matrix)
    self._cons_senses = cons_senses
    self._upper_bounds = None
    self.set_upper_bounds(upper_bounds)

  def build_subproblem(self, *args, **kwargs):
    return Subproblem(self, *args, **kwargs)

  def get_num_rows(self):
    return self._cons_matrix.shape[0]

  def get_num_cols(self):
    return self._cons_matrix.shape[1]

  def _set_cons_matrix(self, m):
    if isinstance(m, np.matrix):
      self._cons_matrix = csr_matrix(m)
    else:
      self._cons_matrix = m

  def set_obj_coefs(self, coefs):
    if isinstance(coefs, (tuple, list)):
      obj = dok_matrix((1, len(coefs)), dtype=np.float16)
      for i, c in enumerate(coefs):
        obj[0, i] = c
    else:
      obj = coefs
    self._obj = SparseVector(obj)

  def get_obj_coefs(self):
    return self._obj

  def get_upper_bounds(self):
    return self._upper_bounds

  def set_upper_bound(self, i, v):
    self._upper_bounds[i] = v

  def set_upper_bounds(self, coefs):
    if isinstance(coefs, dok_matrix):
      self._upper_bounds = SparseVector(coefs)
    elif isinstance(coefs, (tuple, list)):
      m = dok_matrix((1, len(coefs)), dtype=np.float16)
      for i, c in enumerate(coefs):
        m[0, i] = c
      self._upper_bounds = SparseVector(m)
    elif isinstance(coefs, SparseVector):
      self._upper_bounds = coefs
    else:
      raise TypeError()

  def get_cons_matrix(self):
    return self._cons_matrix

  def check_col_solution(self, solution):
    # TODO: solution can be a tuple, list or spmatrix
    if len(solution) != self.get_num_cols():
      raise Exception("%d != %d" % (solution.shape[1], self.get_num_cols()))
    v = self._cons_matrix.dot(solution)
    for i in range(len(v)):
      # TODO: add sense
      if v[i] > self._upper_bounds[i]:
        return False
    return True

class Subproblem(Problem):

  def __init__(self, problem, obj=[], cons_matrix=None, cons_senses=[],
               upper_bounds=[], shared_cols=[]):
    Problem.__init__(self, obj, cons_matrix, cons_senses, upper_bounds)
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
