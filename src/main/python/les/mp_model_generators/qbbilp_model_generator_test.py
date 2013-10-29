#!/usr/bin/env python
#
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

from __future__ import print_function

from les.decomposers import finkelstein_qb_decomposer
from les.mp_model_generators import qbbilp_model_generator
from les.utils import unittest

class QBBILPModelGeneratorTest(unittest.TestCase):

  def setUp(self):
    self._g = qbbilp_model_generator.QBBILPModelGenerator()

  def test_gen_random_model(self):
    model = self._g.gen(num_variables=400, num_constraints=200)
    self.assert_equal(200, model.get_num_constraints())
    self.assert_equal(400, model.get_num_variables())

  def test_gen_random_model_with_fixed_num_blocks(self):
    num_blocks = 3
    model = self._g.gen(num_variables=2, num_constraints=2,
                          num_blocks=num_blocks)
    self.assert_is_none(model)
    model = self._g.gen(num_constraints=6, num_variables=9,
                        num_blocks=num_blocks, fix_block_size=True,
                        separator_size=1)
    decomposer = finkelstein_qb_decomposer.FinkelsteinQBDecomposer(model)
    decomposer.decompose()
    models = decomposer.get_decomposition_tree().get_models()
    self.assert_equal(num_blocks, len(models))

if __name__ == '__main__':
  unittest.main()
