#!/usr/bin/env python
#
# -*- coding: utf-8; -*-
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

import numpy
import unittest

from les.problems.milp_problem import MILPProblem
from les.decomposers.finkelstein_qb_decomposer import FinkelsteinQBDecomposer

class FinkelsteinQBDecomposerTest(unittest.TestCase):

  def test_decompose(self):
    cons_matrix = numpy.matrix([[2., 3., 4., 1., 0., 0., 0., 0., 0.],
                                [1., 2., 3., 2., 0., 0., 0., 0., 0.],
                                [0., 0., 1., 4., 3., 4., 2., 0., 0.],
                                [0., 0., 2., 1., 1., 2., 5., 0., 0.],
                                [0., 0., 0., 0., 0., 0., 2., 1., 2.],
                                [0., 0., 0., 0., 0., 0., 3., 4., 1.],
                                ])
    problem = MILPProblem([8, 2, 5, 5, 8, 3, 9, 7, 6],
                          True,
                          cons_matrix,
                          None,
                          [7, 6, 9, 7, 3, 5])
    decomposer = FinkelsteinQBDecomposer()
    decomposer.decompose(problem)
    u = [set([0, 1]), set([2, 3]), set([4, 5])]
    s = [set([]), set([2, 3]), set([6])]
    m = [set([0, 1]), set([4, 5]), set([8, 7])]
    for t, r in ((u, decomposer._u), (s, decomposer._s), (m, decomposer._m)):
      self.assertEqual(len(t), len(r))
      for i in range(len(t)):
        self.assertEqual(t[i], r[i])

if __name__ == "__main__":
  unittest.main()
