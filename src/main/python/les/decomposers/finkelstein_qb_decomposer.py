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

from les.mp_model import mp_model_parameters
from les.mp_model import mp_model
from les.mp_model import mp_submodel
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
    self._model_params = mp_model_parameters.build(model)

  def _build_decomposition_tree(self):
    # TODO: fix this. Add default empty separators set.
    s = self._s + [set()]
    # TODO: check connectivity order.
    prev_model = mp_submodel.build(self._model,
                                   self._u[-1], s[-2] | self._m[-1] | s[-1])
    tree = DecompositionTree(self._model)
    tree.add_node(prev_model)
    tree.set_root(prev_model)
    for i in xrange(len(self._u) - 2, -1, -1):
      model = mp_submodel.build(self._model,
                                self._u[i], s[i + 1] | self._m[i] | s[i])
      tree.add_node(model)
      tree.add_edge(prev_model, model,
                    [self.get_model().get_variable_by_index(i).get_name()
                     for i in s[i + 1]])
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
    logging.info('Decompose model %s', self._model_params.get_name())
    self._u = []
    self._s = []
    self._m = []
    row_matrix = self._model_params.get_rows_coefficients()
    col_matrix = row_matrix.tocsc()
    all_cols = set(initial_cols)
    prev_cols = set()
    prev_rows = set()
    prev_col_indices = set()
    all_rows = set()
    cntr = 0
    while True:
      prev_cols = set(all_cols)
      all_rows = set()
      all_cols = set()
      for c in prev_cols:
        rows = _get_indices(col_matrix, c)
        for row in rows:
          all_cols.update(_get_indices(row_matrix, row))
        all_rows.update(rows)
      row_indices = all_rows - prev_rows
      if not len(row_indices):
        break
      self._m.append(set())
      col_indices = set()
      for i in row_indices:
        col_indices.update(_get_indices(row_matrix, i))
      self._s.append(col_indices & prev_col_indices)
      self._m[cntr] = col_indices - self._s[cntr]
      self._m[cntr - 1] = self._m[cntr - 1] - self._s[cntr]
      prev_col_indices = set(col_indices)
      self._u.append(row_indices)
      prev_rows = all_rows
      cntr += 1
    self._build_decomposition_tree()
