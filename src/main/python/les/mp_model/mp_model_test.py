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

from les import mp_model
from les.mp_model.formats import mps
from les.utils import unittest

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'mp_model_test_data')

class MPModelTest(unittest.TestCase):

  def build_simple_2x2_model(self):
    x = mp_model.MPVariable(name='x')
    y = mp_model.MPVariable(name='y')
    model = mp_model.build(
      2 * x + 3 * y,
      [4 * x + 6 * y <= 5,
       2 * x + 2 * y <= 4],
    )
    for constraint in model.get_constraints():
      self.assert_equal(set([id(var) for var in constraint.get_variables()]),
                        set([id(x), id(y)]))
    return model

  def build_model_from_mps_file(self, filename):
    if not os.path.exists(filename):
      raise IOError()
    decoder = mps.Decoder()
    with open(filename, 'r') as stream:
      decoder.decode(stream)
    model = mp_model.build(decoder)
    return model

  def test_build_from_expressions(self):
    model = self.build_simple_2x2_model()
    self.assert_equal(2, model.get_num_variables())
    self.assert_equal(2, model.get_num_constraints())

  def test_constraints_management(self):
    model = mp_model.MPModel()
    x = model.add_binary_variable('x')
    y = model.add_binary_variable('y')
    c1 = model.add_constraint(5.0 * x + 3.0 * y <= 7, 'c1')
    self.assert_equal(1, model.get_num_constraints())
    self.assert_true(set([id(var) for var in c1.get_variables()]) ==
                     set([id(x), id(y)]))
    c3 = model.add_constraint(4.0 * x + 6.0 * y <= 5, 'c3')
    c2 = model.add_constraint(2.0 * x + 2.0 * y <= 4, 'c2')
    self.assert_equal([c1, c3, c2], model.get_constraints())

  def test_variables_management(self):
    model = mp_model.MPModel()
    x = model.add_binary_variable('x')
    self.assert_equal('x', x.get_name())
    y = model.add_binary_variable('y')
    self.assert_equal('y', y.get_name())
    z = model.add_binary_variable('z')
    self.assert_equal('z', z.get_name())
    self.assert_equal(3, model.get_num_variables())
    self.assert_equal([x, y, z], model.get_variables())

  def test_build_objective(self):
    model = mp_model.MPModel()
    x = model.add_binary_variable('x')
    y = model.add_binary_variable('y')
    z = model.add_binary_variable('z')
    model.set_objective(3.0 * x + 4.0 * y + 5.0 * z)
    self.assert_equal(3.0 * x + 4.0 * y + 5.0 * z, model.get_objective()._expr)

  def test_is_binary_model(self):
    model = self.build_simple_2x2_model()
    for var in model.get_variables():
      var.set_type(mp_model.MPVariable.BINARY)
    self.assert_true(model.is_binary())

  def test_build_from_scratch1(self):
    model = mp_model.build(
      [1, 2, 3], [[1, 2, 3], [7, 8, 9]], ['L', 'L'], [2, 5])
    self.assert_equal(3, model.get_num_variables())
    self.assert_equal(2, model.get_num_constraints())

  def test_build_from_scratch2(self):
    model = mp_model.build(
      [8, 2, 5, 5, 8, 3, 9, 7, 6],
      [[2, 3, 4, 1, 0, 0, 0, 0, 0],
       [1, 2, 3, 2, 0, 0, 0, 0, 0],
       [0, 0, 1, 4, 3, 4, 2, 0, 0],
       [0, 0, 2, 1, 1, 2, 5, 0, 0],
       [0, 0, 0, 0, 0, 0, 2, 1, 2],
       [0, 0, 0, 0, 0, 0, 3, 4, 1]],
      ['L'] * 6,
      [7, 6, 9, 7, 3, 5]
    )
    self.assert_equal(9, model.get_num_variables())
    self.assert_equal(6, model.get_num_constraints())

  def test_build_from_test_mps(self):
    model = self.build_model_from_mps_file(os.path.join(TEST_DATA_DIR,
                                                            'test.mps'))
    self.assert_equal(7, model.get_num_variables())
    self.assert_equal(4, model.get_num_constraints())

  def test_build_from_10teams_mps(self):
    model = self.build_model_from_mps_file(os.path.join(TEST_DATA_DIR,
                                                            '10teams.mps'))
    self.assert_equal(2025, model.get_num_variables())
    self.assert_equal(230, model.get_num_constraints())

if __name__ == '__main__':
  unittest.main()
