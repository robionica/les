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

from __future__ import absolute_import

from les.mp_model import mp_solution
from les.utils import unittest

class MPSolutionTest(unittest.TestCase):

  def test_basic_manimulations(self):
    solution = mp_solution.MPSolution()
    solution.set_variables_values(('x1', 'x2'), (1, 2))
    self.assert_equal(['x1', 'x2'], solution.get_variables_names())
    self.assert_equal([1, 2], solution.get_variables_values().copy_to_list())

  def test_merge(self):
    solution1 = mp_solution.MPSolution()
    solution1.set_variables_values(('x1', 'x2', 'x3', 'x4'), (1, 1, 0, 0))
    self.assert_equal([0, 1],
                      solution1.get_variables_values().get_entries_indices())
    solution2 = mp_solution.MPSolution()
    solution2.set_variables_values(['x1', 'x2', 'x3', 'x4'], (1, 0, 1, 1))
    solution1.update_variables_values(solution2)
    self.assert_equal(['x1', 'x2', 'x3', 'x4'], solution1.get_variables_names())
    self.assert_equal([1, 1, 1, 1],
                      solution1.get_variables_values().copy_to_list())

if __name__ == '__main__':
  unittest.main()
