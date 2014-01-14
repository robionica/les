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

import StringIO

from les.mp_model import mp_model_builder
from les.mp_model.mp_model_builder.formats import mps
from les.utils import unittest


class EncoderTest(unittest.TestCase):

  def test_encode(self):
    model1 = mp_model_builder.MPModelBuilder.build_from(
      [8, 2, 5, 5, 8, 3, 9, 7, 6],
      [[2, 3, 4, 1, 0, 0, 0, 0, 0],
       [1, 2, 3, 2, 0, 0, 0, 0, 0],
       [0, 0, 1, 4, 3, 4, 2, 0, 0],
       [0, 0, 2, 1, 1, 2, 5, 0, 0],
       [0, 0, 0, 0, 0, 0, 2, 1, 2],
       [0, 0, 0, 0, 0, 0, 3, 4, 1]],
      ['L'] * 6,
      [7, 6, 9, 7, 3, 5])
    model1.set_name('DEMO1')
    model1.set_objective_name('PRODUCT')
    stream = StringIO.StringIO()
    mps.encode(stream, model1)
    model2 = mp_model_builder.MPModelBuilder.build_from(mps.decode(stream))
    self.assert_equal(model1.get_name(), model2.get_name())
    self.assert_equal(model1.get_num_columns(), model2.get_num_columns())
    self.assert_equal(model1.get_num_rows(), model2.get_num_rows())


if __name__ == '__main__':
  unittest.main()
