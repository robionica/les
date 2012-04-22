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

import os
from scipy import sparse

from les.mp_model.formats import mps
from les.utils import unittest

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'mps_test_data')

class ReaderTest(unittest.TestCase):

  def test_read_test1_mps(self):
    test1_filename = os.path.join(TEST_DATA_DIR, 'test1.mps')
    reader = mps.read(test1_filename)
    self.assert_equal('TESTPROB', reader.get_name())
    self.assert_equal(['L', 'G', 'E'], reader.get_rows_senses())
    self.assert_equal(['X', 'Y', 'Z'], reader.get_columns_names())
    self.assert_equal(['LIM1', 'LIM2', 'LIM3'], reader.get_rows_names())
    self.assert_equal([5.0, 10.0, 7.0], reader.get_rows_rhs())
    self.assert_equal([1.0, 4.0, 9.0], reader.get_objective_coefficients())
    rows_coefs = sparse.lil_matrix([[1.0,  1.0, 0.0],
                                    [1.0,  0.0, 1.0],
                                    [0.0, -1.0, 1.0]])
    # TODO(d2rk): compare matrices.

  def test_read_10teams_mps(self):
    test1_filename = os.path.join(TEST_DATA_DIR, '10teams.mps')
    reader = mps.read(test1_filename)
    self.assert_equal('10teams', reader.get_name())
    self.assert_equal(2025, len(reader.get_objective_coefficients()))
    self.assert_equal(230, reader.get_rows_coefficients().shape[0])
    self.assert_equal(230, len(reader.get_rows_rhs()))

if __name__ == '__main__':
  unittest.main()
