#!/usr/bin/env python
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

from les.mp_model import MPModel
from les.mp_model import MPModelBuilder
from les.utils import unittest


class ModelTest(unittest.TestCase):

  def test_build(self):
    model = MPModelBuilder.build_from_scratch(
      [8, 2, 5, 5, 8, 3, 9, 7, 6],
      [[2., 3., 4., 1., 0., 0., 0., 0., 0.],
       [1., 2., 3., 2., 0., 0., 0., 0., 0.],
       [0., 0., 1., 4., 3., 4., 2., 0., 0.],
       [0., 0., 2., 1., 1., 2., 5., 0., 0.],
       [0., 0., 0., 0., 0., 0., 2., 1., 2.],
       [0., 0., 0., 0., 0., 0., 3., 4., 1.]],
      ["L"] * 6,
      [7, 6, 9, 7, 3, 5])
    self.assert_equal(9, model.get_num_columns())
    self.assert_equal(6, model.get_num_rows())
    self.assert_equal(["c1", "c2", "c3", "c4", "c5", "c6"], model.rows_names)
    self.assert_equal([8, 2, 5, 5, 8, 3, 9, 7, 6],
                      model.get_objective_coefficients())
    self.assert_equal(["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"],
                      model.columns_names)
    self.assert_equal([0.0] * 9, model.columns_lower_bounds)
    self.assert_equal([1.0] * 9, model.columns_upper_bounds)

if __name__ == "__main__":
  unittest.main()
