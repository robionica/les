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

import unittest

from les.problems.bilp_problem import BILPProblem
from les.decomposers.finkelstein_qb_decomposer import FinkelsteinQBDecomposer

class FinkelsteinQBDecomposerTest(unittest.TestCase):

  def test_decompose1(self):
    problem = BILPProblem.build_from_scratch(
      [8, 2, 5, 5, 8, 3, 9, 7, 6],
      [[2., 3., 4., 1., 0., 0., 0., 0., 0.],
       [1., 2., 3., 2., 0., 0., 0., 0., 0.],
       [0., 0., 1., 4., 3., 4., 2., 0., 0.],
       [0., 0., 2., 1., 1., 2., 5., 0., 0.],
       [0., 0., 0., 0., 0., 0., 2., 1., 2.],
       [0., 0., 0., 0., 0., 0., 3., 4., 1.]],
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

  def test_decompose2(self):
    problem = BILPProblem.build_from_scratch(
      [2, 3, 1, 5, 4, 6, 1],
      [[3., 4., 1., 0., 0., 0., 0.],
       [0., 2., 3., 3., 0., 0., 0.],
       [0., 2., 0., 0., 3., 0., 0.],
       [0., 0., 2., 0., 0., 3., 2.]],
      [6, 5, 4, 5])
    decomposer = FinkelsteinQBDecomposer()
    decomposer.decompose(problem)
    u = [set([0]), set([1, 2, 3])]
    s = [set([]), set([1, 2])]
    m = [set([0]), set([3, 4, 5, 6])]
    for t, r in ((u, decomposer._u), (s, decomposer._s), (m, decomposer._m)):
      self.assertEqual(len(t), len(r))
      for i in range(len(t)):
        self.assertEqual(t[i], r[i])

  def test_decompose3(self):
    problem = BILPProblem.build_from_scratch(
      [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2],
      [[ 4.,  0.,  1.,  1.,  3.,  1.,  3.,  0.,  3.,  1., 2.,  0.,  3.,  2.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 2.,  0.,  2.,  2.,  4.,  0.,  3.,  1.,  1.,  0., 1.,  6.,  1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 0.,  1.,  2.,  1.,  3.,  1.,  1.,  2.,  4.,  6., 0.,  2.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.],
       [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0., 2.,  1.,  2.,  1.,  2.,  0.,  4.,  1.,  2.,  2.],
       [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0., 0.,  3.,  1.,  2.,  2.,  3.,  0.,  2.,  4.,  0.]],
      [6, 5, 4, 5, 6])
    decomposer = FinkelsteinQBDecomposer()
    decomposer.decompose(problem)

if __name__ == '__main__':
  unittest.main()
