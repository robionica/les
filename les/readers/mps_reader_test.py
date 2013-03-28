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
import unittest

from les.readers.mps_reader import MPSReader

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "mps_reader_test_data")

class MPSReaderTest(unittest.TestCase):

  def test_parse_test1(self):
    test1_filename = os.path.join(TEST_DATA_DIR, "test1.mps")
    reader = MPSReader()
    with open(test1_filename, "r") as stream:
      reader.parse(stream)
    self.assertEqual("TESTPROB", reader.get_name())
    self.assertEqual([[0.0, 5.0, 10.0, 7.0]], reader.get_rhs())
    self.assertEqual([(0, 0, 1.0), (1, 0, 1.0), (2, 0, 1.0), (0, 1, 4.0),
                      (1, 1, 1.0), (3, 1, -1.0), (0, 2, 9.0), (2, 2, 1.0),
                      (3, 2, 1.0)], reader.get_con_coefs())
    self.assertEqual(['N', 'L', 'G', 'E'], reader.get_rows_senses())

if __name__ == "__main__":
  unittest.main()
