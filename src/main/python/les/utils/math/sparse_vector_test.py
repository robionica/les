from les.utils import unittest
from les.base import sparse_vector

class SparseVectorTest(unittest.TestCase):

  def test_misc_manipulations(self):
    vector = sparse_vector.SparseVector([1, 0, 3])
    self.assert_equal(3, vector.get_size())
    self.assert_equal(2, vector.get_num_entries())
    self.assert_equal([0, 2], vector.get_entries_indices())
    self.assert_equal([1, 0, 3], vector.copy_to_list())

if __name__ == '__main__':
  unittest.main()
