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

'''The Finkelstein's quasi-block decomposition algorithm is represented by
:class:`FinkelsteinQBDecomposer` class.

The following snippet shows how to create a simple :class:`~les.model.Model`
instance with quasi-block structure and decompose it with help of Finkelstein's
algorithm::

  model = model.build_from_scratch(
    [8, 2, 5, 5, 8, 3, 9, 7, 6],
    [[2, 3, 4, 1, 0, 0, 0, 0, 0],
     [1, 2, 3, 2, 0, 0, 0, 0, 0],
     [0, 0, 1, 4, 3, 4, 2, 0, 0],
     [0, 0, 2, 1, 1, 2, 5, 0, 0],
     [0, 0, 0, 0, 0, 0, 2, 1, 2],
     [0, 0, 0, 0, 0, 0, 3, 4, 1]],
    [7, 6, 9, 7, 3, 5]
  )
  decomposer = FinkelsteinQBDecomposer(model)
  decomposer.decompose()

Once the model has been decomposed, its
:class:`~les.decomposition_tree.DecompositionTree` can be obtained with help of
:func:`get_decomposition_tree` method.
'''

# +---------+------+
# |         |      |
# +---------+------+------------+---+
# ^         |      |            |   |
# |         +------+------------+---+---------+
# |         ^      ^            |   |         |
# |         |      |            +---+---------+
# |         |      |            ^   ^         ^
# |   M     |  S   |     M      | S |    M    |
#

import networkx

from les.mp_model import MPModel
from les.decomposers import decomposer_base
from les.graphs.decomposition_tree import DecompositionTree
from les.utils import logging

def _get_indices(m, i):
  start = m.indptr[i]
  size = m.indptr[i + 1] - start
  result = []
  for j in xrange(start, start + size):
    result.append(m.indices[j])
  return result


class FinkelsteinQBDecomposer(decomposer_base.DecomposerBase):
  '''This class represents Finkelstein QB decomposer for MP problems.

  :param model: A :class:`~les.mp_model.mp_model.MPModel` based model instance.
  '''

  def __init__(self, model):
    decomposer_base.DecomposerBase.__init__(self, model)
    self._u = []
    self._s = []
    self._m = []

  def _build_decomposition_tree(self):
    # TODO: fix this. Add default empty separators set.
    s = self._s + [set()]
    # TODO: check connectivity order.
    prev_model = self._model.slice(self._u[-1], s[-2] | self._m[-1] | s[-1])
    tree = DecompositionTree(self._model)
    tree.add_node(prev_model)
    tree.set_root(prev_model)
    for i in xrange(len(self._u) - 2, -1, -1):
      model = self._model.slice(self._u[i], s[i + 1] | self._m[i] | s[i])
      tree.add_node(model)
      tree.add_edge(prev_model, model,
                    [self.get_model().get_columns_names()[i] for i in s[i + 1]])
      prev_model = model
    self._decomposition_tree = tree

  def decompose(self, initial_cols=[0], max_separator_size=0,
                merge_empty_blocks=True):
    '''Decomposes model into submodels starting by initial cols. By default
    starts from column 0. Default max separator size is 11.

    :param initial_cols: A list of integers.
    :param max_separator_size: An integer that represents max available
      separator size.
    :param merge_empty_blocks: ``True`` or ``False``, whether or not we need to
      merge empty blocks.
    '''
    if max_separator_size:
      raise NotImplementedError()
    logging.info('Decompose model %s', self._model.get_name())

    m = self._model.get_rows_coefficients()

    j_to_i_mapping = {}
    for j in range(m.shape[1]):
      j_to_i_mapping[j] = set()

    # TODO(d2rk): use interaction graph?
    g = networkx.Graph()
    g.add_nodes_from(range(m.shape[1]))
    for i in xrange(m.shape[0]):
      J_ = _get_indices(m, i)
      for j in range(len(J_) - 1):
        j_to_i_mapping[J_[j]].add(i)
        for j_ in range(j + 1, len(J_)):
          g.add_edge(J_[j], J_[j_])
      j_to_i_mapping[J_[-1]].add(i)

    def get_neighbors(nodes):
      neighbors = set()
      for node in nodes:
        neighbors.update(g.neighbors(node))
      return neighbors

    self._m = [set(initial_cols) | get_neighbors(set(initial_cols))]
    self._s = [set()]
    self._u = [set()]

    i = len(self._m)
    J = get_neighbors(self._m[i - 1])
    while True:
      M_ = J - self._m[i - 1] - self._s[i - 1]
      if not len(M_):
        break
      T = get_neighbors(M_)
      J_ = T - M_
      self._m.append(M_)
      self._u.append(set())
      self._s.append(J_ & J)
      self._m[i - 1] -= self._s[i]
      for j in self._m[i - 1]:
        self._u[i - 1].update(j_to_i_mapping[j])
      J = T
      i += 1
    for j in self._m[i - 1]:
      self._u[i - 1].update(j_to_i_mapping[j])

    self._build_decomposition_tree()
