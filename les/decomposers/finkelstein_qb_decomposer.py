# -*- coding: utf-8; -*-
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

#
# +---------+------+
# |         |      |
# +---------+------+------------+---+
# ^         |      |            |   |
# |         +------+------------+---+---------+
# |         ^      ^            |   |         |
# |         |      |            +---+---------+
# |         |      |            ^   ^         ^
# |   M     |  S   |     M      | S |    M    |
#

import numpy as np
from scipy.sparse import csr_matrix, vstack, dok_matrix

from les.decomposers.decomposer import Decomposer
from les.decomposition_tree import DecompositionTree
from les.problems.milp_problem import MILPProblem
from les.sparse_vector import SparseVector

class FinkelsteinQBDecomposer(Decomposer):
  """This class represents Finkelstein QB decomposer for MILP problems."""

  def __init__(self):
    self._u = []
    self._s = []
    self._m = []
    self._decomposition_tree = None

  def _set_problem(self, problem):
    if not isinstance(problem, MILPProblem):
      raise TypeError("problem must be derived from MILPProblem: %s",
                      type(problem))
    super(FinkelsteinQBDecomposer, self)._set_problem(problem)

  def _build_subproblem(self, rows, left_cols, middle_cols, right_cols):
    cols = left_cols | middle_cols | right_cols
    problem = self.get_problem()
    # Put rows one under one
    cons_matrix = vstack([problem.get_cons_matrix().getrow(i) for i in rows],
                         format="csr")
    # Build sparse vector of obj function coefs
    # TODO: copy dtype
    obj = SparseVector((1, problem.get_num_cols()), dtype=np.float16)
    for i in cols:
      obj[i] = problem.get_obj_coefs()[i]
    # Build sparse vector of upper bounds
    upper_bounds = [problem.get_rows_upper_bounds()[i] for i in rows]
    # Build subproblem
    sp = problem.build_subproblem(obj, True, cons_matrix, [], upper_bounds,
                                    shared_cols=left_cols | right_cols)
    return sp

  def _build_decomposition_tree(self):
    # TODO: fix this. Add default empty separators set.
    s = self._s + [set()]
    # Build subproblems and connect them
    # TODO: check connectivity order
    prev_problem = self._build_subproblem(self._u[0], s[0], self._m[0], s[1])
    tree = DecompositionTree(self.get_problem(), root=prev_problem)
    for i in range(1, len(self._u)):
      problem = self._build_subproblem(self._u[i], s[i], self._m[i], s[i + 1])
      tree.add_node(problem)
      tree.add_edge(prev_problem, problem, s[i])
      prev_problem = problem
    self._decomposition_tree = tree

  def decompose(self, problem, initial_cols=[0], max_separator_size=0,
                merge_empty_blocks=True):
    """Decomposes problem into subproblems starting by initial cols. By default
    starts from column 0.
    """
    self._set_problem(problem)
    self._u = []
    self._s = []
    self._m = []
    matrix = problem.get_cons_matrix().tolil()
    all_cols = set(initial_cols)
    prev_cols = set()
    prev_rows = set()
    prev_col_indices = set()
    all_rows = set()
    rows_by_cols = dict() # cache
    cols_by_rows = dict() # cache
    cntr = 0
    while True:
      prev_cols = set(all_cols)
      all_rows = set()
      all_cols = set()
      for c in prev_cols:
        rows = rows_by_cols.setdefault(c, matrix.getcol(c).nonzero()[0])
        for row in rows:
          all_cols.update(cols_by_rows.setdefault(row, matrix.getrow(row).nonzero()[1]))
        all_rows.update(rows)
      row_indices = all_rows - prev_rows
      if not len(row_indices):
        break
      self._m.append(set())
      col_indices = set()
      for i in row_indices:
        col_indices.update(cols_by_rows[i])
      self._s.append(col_indices & prev_col_indices)
      self._m[cntr] = col_indices - self._s[cntr]
      self._m[cntr - 1] = self._m[cntr - 1] - self._s[cntr]
      prev_col_indices = set(col_indices)
      self._u.append(row_indices)
      prev_rows = all_rows
      cntr += 1
    self._build_decomposition_tree()

  def get_decomposition_tree(self):
    return self._decomposition_tree
