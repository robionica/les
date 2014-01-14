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

from scipy import sparse

from les.mp_model import mp_model_builder
from les.graphs import decomposition_tree
from les.utils import unittest


class DecompositionTreeTest(unittest.TestCase):

  def test_dependencies(self):
    builder = mp_model_builder.MPModelBuilder()
    x1, x2, x3, x4, x5, x6, x7, x8, x9 = (builder.add_binary_variable("x%d" % i)
                                          for i in range(9))
    builder.maximize(8 * x1 + 2 * x2 + 5 * x3 + 5 * x4 + 8 * x5 + 3 * x6
                     + 9 * x7 + 7 * x8 + 6 * x9)
    builder.set_constraints([2 * x1 + 3 * x2 + 4 * x3 + x4 <= 7,
                             x1 + 2 * x2 + 3 * x3 + 2 * x4 <= 6,
                             x3 + 4 * x4 + 3 * x5 + 4 * x6 + 2 * x7 <= 9,
                             2 * x3 + x4 + x5 + 2 * x6 + 5 * x7 <= 7,
                             2 * x7 + x8 + 2 * x9 <= 3,
                             3 * x7 + 4 * x8 + x9 <= 5])
    model = builder.build()
    builder = mp_model_builder.MPModelBuilder()
    x1, x2, x3, x4 = (builder.add_binary_variable("x%d" % i) for i in range(4))
    builder.set_objective(8 * x1 + 2 * x2 + 5 * x3 + 5 * x4)
    builder.set_constraints([2. * x1 + 3. * x2 + 4. * x3 + 1. * x4 <= 7,
                             1. * x1 + 2. * x2 + 3. * x3 + 2. * x4 <= 6])
    submodel1 = builder.build()
    builder = mp_model_builder.MPModelBuilder()
    x3, x4, x5, x6, x7 = (builder.add_binary_variable("x%d" % i) for i in range(3, 8))
    builder.set_objective(5 * x3 + 5 * x4 + 8 * x5 + 3 * x6 + 9 * x7)
    builder.set_constraints([2. * x3 + 1. * x4 + 3. * x5 + 4. * x6 + 2. * x7 <= 9,
                             2. * x3 + 1. * x4 + 1. * x5 + 2. * x6 + 5. * x7 <= 7])
    submodel2 = builder.build()
    builder = mp_model_builder.MPModelBuilder()
    x7, x8, x9 = (builder.add_binary_variable("x%d" % i) for i in range(7, 10))
    builder.set_objective(9 * x7 + 7 * x8 + 6 * x9)
    builder.set_constraints([2. * x7 + 1. * x8 + 2. * x9 <= 3,
                             3. * x7 + 4. * x8 + 1. * x9 <= 5])
    submodel3 = builder.build()
    tree = decomposition_tree.DecompositionTree(model=model)
    tree.add_node(submodel3)
    tree.set_root(submodel3)
    self.assert_equal(1, tree.get_num_nodes())
    node3 = tree.node[submodel3.get_name()]
    self.assert_equal(set(), node3.get_shared_variables())
    node2 = tree.add_node(submodel2)
    node1 = tree.add_node(submodel1)
    self.assert_equal(3, tree.get_num_nodes())
    self.assert_equal(submodel3.get_name(), tree.get_root())
    edge1 = tree.add_edge(submodel3, submodel2, shared_variables=[u'x7'])
    self.assert_equal(set([u'x7']), node3.get_shared_variables())
    self.assert_equal(set([u'x8', u'x9']), node3.get_local_variables())
    self.assert_equal(set([u'x3', u'x4', u'x5', u'x6']),
                      node2.get_local_variables())
    tree.add_edge(submodel2, submodel1, shared_variables=[u'x3', u'x4'])
    self.assert_equal(set([u'x5', u'x6']), node2.get_local_variables())


if __name__ == '__main__':
  unittest.main()
