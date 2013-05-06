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

from les.problems.qbbilp_problem_generator import QBBILPProblemGenerator
from les.utils import unittest

class QBBILPProblemGeneratorTest(unittest.TestCase):

  def test_gen(self):
    generator = QBBILPProblemGenerator()
    problem = generator.gen(200, 400)
    self.assert_equal(200, problem.get_num_constraints())
    self.assert_equal(400, problem.get_num_variables())
