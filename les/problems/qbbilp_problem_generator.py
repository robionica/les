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

from scipy import sparse
import numpy
import random

from les.problems.bilp_problem import BILPProblem

class _Block(object):

  def __init__(self, num_rows, num_cols, left_sep_size=0, right_sep_size=0):
    self.num_rows = num_rows
    self.num_cols = num_cols
    self.left_sep_size = left_sep_size
    self.right_sep_size = right_sep_size

  def __str__(self):
    return "Block[num_rows=%d, num_cols=%d, left_sep_size=%d, right_sep_size=%d]" \
        % (self.num_rows, self.num_cols, self.left_sep_size, self.right_sep_size)

class QBBILPProblemGenerator(object):

  def gen(self, num_rows, num_cols, dtype=numpy.float16,
          max_separator_size=10, fixed_separator_size=False,
          max_num_block_rows=10, fixed_num_block_rows=False,
          max_num_block_cols=10, fixed_num_block_cols=False):
    self._matrix = sparse.dok_matrix((num_rows, num_cols), dtype=dtype)
    self._rhs = [0.0] * num_rows
    blocks = []
    ar = num_rows
    ac = num_cols
    while ar > 1 and ac > 3:
      nr = random.randint(1, round(ar / 1.5))
      try:
        nc = random.randint(3, (ac * nr) / ar)
      except ValueError:
        nc = ac
      blocks.append(_Block(nr, nc))
      ar -= nr
      ac -= nc
    blocks[-1].num_rows += ar
    blocks[-1].num_cols += ac
    # Start filling the matrix and rhs
    self._row_offset = 0
    self._col_offset = 0
    for i in xrange(len(blocks) - 1):
      sep_size = random.randint(
        1,
        min((min([blocks[i].num_cols, blocks[i + 1].num_cols]) / 2),
            max_separator_size / 2)
      )
      blocks[i].right_sep_size = blocks[i + 1].left_sep_size = sep_size
      self._fill_block(blocks[i])
    self._fill_block(blocks[-1])
    # Build and return problem
    return BILPProblem.build_from_scratch(
      [random.randint(1, num_cols) for i in xrange(num_cols)],
      self._matrix.tocsr(),
      [],
      self._rhs
    )

  def _fill_block(self, b):
    num_cols = b.num_cols + b.right_sep_size
    s = num_cols * random.randint(1, 5)
    c = numpy.random.multinomial(s, [1. / num_cols for i in xrange(num_cols)],
                                 size=b.num_rows)
    # Fix matrix, reduce zeros
    c += 1.
    s += num_cols
    for i in xrange(b.num_rows):
      for j in xrange(num_cols):
        self._matrix[self._row_offset + i, self._col_offset + j] = c[i, j]
      self._rhs[self._row_offset + i] = s / (1.5 + random.random())
    self._row_offset += b.num_rows
    self._col_offset += b.num_cols
