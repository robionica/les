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

from les import mp_model
from les.mp_model import mp_model_parameters
from les.utils import unittest

class ModelParametersTest(unittest.TestCase):

  def test_build(self):
    model = mp_model.build(
      [8, 2, 5, 5, 8, 3, 9, 7, 6],
      [[2., 3., 4., 1., 0., 0., 0., 0., 0.],
       [1., 2., 3., 2., 0., 0., 0., 0., 0.],
       [0., 0., 1., 4., 3., 4., 2., 0., 0.],
       [0., 0., 2., 1., 1., 2., 5., 0., 0.],
       [0., 0., 0., 0., 0., 0., 2., 1., 2.],
       [0., 0., 0., 0., 0., 0., 3., 4., 1.]],
      ['L'] * 6,
      [7, 6, 9, 7, 3, 5]
    )
    params = mp_model_parameters.build(model)
    self.assert_equal(9, params.get_num_columns())
    self.assert_equal(6, params.get_num_rows())
    self.assert_equal([8, 2, 5, 5, 8, 3, 9, 7, 6],
                      params.get_objective_coefficients())
    self.assert_equal(['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8', 'x9'],
                      params.get_columns_names())

if __name__ == '__main__':
  unittest.main()
