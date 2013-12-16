#!/usr/bin/env python
#
# Copyright (c) 2013 Oleksandr Sviridenko
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

from __future__ import with_statement

import os

from les.mp_model import MPModel
from les.mp_model.mp_model_builder import MPModelBuilder
from les.mp_model.mp_model_builder import MPVariable
from les.mp_model.mp_model_builder.formats import mps
from les.utils import unittest


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "..",
                             "mp_model_test_data")


class MPModelTest(unittest.TestCase):

  def test_build_simple_2x2_model(self):
    builder = MPModelBuilder()
    x1, x2 = builder.x1(), builder.x2()
    builder.set_objective(2 * x1 + 3 * x2)
    builder.set_constraints([4 * x1 + 6 * x2 <= 5,
                             2 * x1 + 2 * x2 <= 4])
    for constraint in builder.get_constraints():
      self.assert_equal(set([id(var) for var in constraint.get_variables()]),
                        set([id(x1), id(x2)]))
    self.assert_equal(2, builder.get_num_variables())
    self.assert_equal(2, builder.get_num_constraints())
    for var in builder.get_variables():
      var.set_type(MPVariable.BINARY)
    self.assert_true(builder.is_binary())

  def build_model_from_mps_file(self, filename):
    if not os.path.exists(filename):
      raise IOError("Path doesn't exist: %s" % filename)
    decoder = mps.Decoder()
    with open(filename, "r") as stream:
      decoder.decode(stream)
    return MPModelBuilder.build_from(decoder)

  def test_constraints_management(self):
    builder = MPModelBuilder()
    x = builder.add_binary_variable("x")
    y = builder.add_binary_variable("y")
    c1 = builder.add_constraint(5.0 * x + 3.0 * y <= 7, "c1")
    self.assert_equal(1, builder.get_num_constraints())
    self.assert_true(set([id(var) for var in c1.get_variables()]) ==
                     set([id(x), id(y)]))
    c3 = builder.add_constraint(4.0 * x + 6.0 * y <= 5, "c3")
    c2 = builder.add_constraint(2.0 * x + 2.0 * y <= 4, "c2")
    self.assert_equal([c1, c3, c2], builder.get_constraints())

  def test_variables_management(self):
    builder = MPModelBuilder()
    x = builder.add_binary_variable('x')
    self.assert_equal('x', x.get_name())
    y = builder.add_binary_variable('y')
    self.assert_equal('y', y.get_name())
    z = builder.add_binary_variable('z')
    self.assert_equal('z', z.get_name())
    self.assert_equal(3, builder.get_num_variables())
    self.assert_equal([x, y, z], builder.get_variables())

  def test_objective_management(self):
    builder = MPModelBuilder()
    x = builder.add_binary_variable('x')
    y = builder.add_binary_variable('y')
    z = builder.add_binary_variable('z')
    builder.set_objective(3.0 * x + 4.0 * y + 5.0 * z)
    self.assert_equal(3.0 * x + 4.0 * y + 5.0 * z, builder.get_objective()._expr)

  def test_build_from_scratch1(self):
    model = MPModelBuilder.build_from_scratch(
      [1, 2, 3], [[1, 2, 3], [7, 8, 9]], ['L', 'L'], [2, 5])
    self.assert_equal(3, model.get_num_columns())
    self.assert_equal(2, model.get_num_rows())

  def test_build_from_scratch2(self):
    model = MPModelBuilder.build_from_scratch(
      [8, 2, 5, 5, 8, 3, 9, 7, 6],
      [[2, 3, 4, 1, 0, 0, 0, 0, 0],
       [1, 2, 3, 2, 0, 0, 0, 0, 0],
       [0, 0, 1, 4, 3, 4, 2, 0, 0],
       [0, 0, 2, 1, 1, 2, 5, 0, 0],
       [0, 0, 0, 0, 0, 0, 2, 1, 2],
       [0, 0, 0, 0, 0, 0, 3, 4, 1]],
      ['L'] * 6,
      [7, 6, 9, 7, 3, 5])
    self.assert_equal(9, model.get_num_columns())
    self.assert_equal(6, model.get_num_rows())

  def test_build_from_test_mps(self):
    model = self.build_model_from_mps_file(os.path.join(TEST_DATA_DIR,
                                                        'test.mps'))
    self.assert_equal(7, model.get_num_columns())
    self.assert_equal(["X%d" % (_ + 1,) for _ in range(7)], model.get_columns_names())
    self.assert_equal(4, model.get_num_rows())

  def etest_build_from_10teams_mps(self):
    model = self.build_model_from_mps_file(os.path.join(TEST_DATA_DIR,
                                                        '10teams.mps'))
    self.assert_equal(2025, model.get_num_columns())
    self.assert_equal(230, model.get_num_rows())


if __name__ == '__main__':
  unittest.main()
