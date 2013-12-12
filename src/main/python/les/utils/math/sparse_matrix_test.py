#!/usr/bin/env python

from scipy import sparse

from les.utils import unittest

class SparseColumnOrderedMatrixTest(unittest.TestCase):

  def test_columns_indices(self):
    matrix = sparse.csc_matrix(([1, 2, 3, 4, 5, 6, 7],
                                ([0, 2, 2, 0, 1, 2, 1], [0, 0, 1, 2, 2, 2, 3])),
                               shape=(3, 4))
    # TODO(d2rk):...

if __name__ == '__main__':
  unittest.main()
