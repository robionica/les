import random

from scipy import sparse
import numpy

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
      nr = random.randint(1, ar / 2)
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
    for i in range(len(blocks) - 1):
      sep_size = random.randint(
        1,
        min((min([blocks[i].num_cols, blocks[i + 1].num_cols]) / 2),
            max_separator_size / 2)
      )
      blocks[i].right_sep_size = blocks[i + 1].left_sep_size = sep_size
      self._fill_block(blocks[i])
    self._fill_block(blocks[-1])
    # Build and return problem
    return BILPProblem([random.randint(1, num_cols) for i in range(num_cols)],
                       True,
                       self._matrix.tocsr(),
                       [],
                       self._rhs,
                       [])

  def _fill_block(self, b):
    num_cols = b.num_cols + b.right_sep_size
    s = num_cols * random.randint(1, 5)
    c = numpy.random.multinomial(s, [1. / num_cols for i in range(num_cols)],
                                 size=b.num_rows)
    # Fix matrix, reduce zeros
    c += 1.
    s += num_cols
    for i in range(b.num_rows):
      for j in range(num_cols):
        self._matrix[self._row_offset + i, self._col_offset + j] = c[i, j]
      self._rhs[self._row_offset + i] = s / (1.5 + random.random())
    self._row_offset += b.num_rows
    self._col_offset += b.num_cols

if __name__ == "__main__":
  g = QBBILPProblemGenerator()
  p = g.gen(6, 9)
  print p.get_cons_matrix().todense()
